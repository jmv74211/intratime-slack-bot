import requests
import json
import urllib.parse

from flask import Flask, jsonify, request, make_response
from http import HTTPStatus

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db import user
from intratime_slack_bot.lib import messages, warehouse, slack, intratime, codes, time_utils, crypt, slack_ui

app = Flask(__name__)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.ECHO_REQUEST, methods=['GET'])
def echo():
    return jsonify({'result': messages.ALIVE_MESSAGE})

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.INTERACTIVE_REQUEST, methods=['POST'])
def get_interactive_data():
    data = urllib.parse.unquote(request.get_data().decode('utf-8'))

    data = json.loads(data.replace('payload=', ''))  # Clean string to convert it to json format

    if data['callback_id'] == slack.CLOCK_CALLBACK:
        if not user.user_exist(data['user']['id']):
            return jsonify(slack.CLOCKING_USER_NOT_FOUND), 200

        user_data = user.get_user_data(data['user']['id'])

        if not intratime.check_user_credentials(user_data['intratime_mail'], crypt.decrypt(user_data['password'])):
            return jsonify(slack.BAD_BD_CREDENTIALS), 200

        # Clock the action
        token = intratime.get_auth_token(user_data['intratime_mail'], crypt.decrypt(user_data['password']))

        request_status = intratime.clocking(data['submission']['action'], token, user_data['intratime_mail'])

        if request_status != codes.SUCCESS:
            slack.post_ephemeral_response_message(messages.set_custom_message('CLOCKING_ERROR', [request_status]),
                                                  data['response_url'])
            return make_response('', 200)

        # Check the clock action in user history
        clocking_check = intratime.get_user_clocks(token, time_utils.get_past_datetime_from_current_datetime(10),
                                                   time_utils.get_current_date_time(), data['submission']['action'])
        if len(clocking_check) == 0:
            slack.post_ephemeral_response_message(messages.set_custom_message('CLOCKING_CHECK_ERROR', [request_status]),
                                                  data['response_url'])
            return make_response('', 200)

        clock_message = slack.generate_clock_message({'intratime_mail': user_data['intratime_mail'],
                                                      'datetime': time_utils.get_current_date_time(),
                                                      'action': data['submission']['action']})
        slack.post_ephemeral_response_message(clock_message, data['response_url'], 'blocks')

    elif data['callback_id'] == slack.ADD_USER_CALLBACK:

        # Check if the user already exists
        if user.user_exist(data['user']['id']):
            return jsonify(slack.USER_ALREADY_REGISTERED_MESSAGE), 200

        # Validate credentials
        if not intratime.check_user_credentials(data['submission']['email'], data['submission']['password']):
            return jsonify(slack.BAD_CREDENTIALS), 200

        cyphered_password = crypt.encrypt(data['submission']['password'])

        # Create new user in user service
        request_status = user.add_user({"user_id": data['user']['id'], "username": data['user']['name'],
                                        "password": cyphered_password,
                                        "intratime_mail": data['submission']['email'],
                                        "registration_date": time_utils.get_current_date_time(),
                                        "last_registration_date": time_utils.get_current_date_time()
                                        })

        if request_status != codes.SUCCESS:
            slack.post_ephemeral_response_message(messages.set_custom_message('ADD_USER_ERROR', [request_status]),
                                                  data['response_url'])
            return make_response('', 200)

        slack.post_ephemeral_response_message(messages.ADD_USER_SUCCESS, data['response_url'])

    elif data['callback_id'] == slack.UPDATE_USER_CALLBACK:

        # Validate credentials
        if not intratime.check_user_credentials(data['submission']['email'], data['submission']['password']):
            return jsonify(slack.BAD_CREDENTIALS), 200

        user_data = user.get_user_data(data['user']['id'])

        if user_data == codes.USER_NOT_FOUND:
            return jsonify(slack.UPDATE_USER_NOT_FOUND), 200

        user_data['intratime_mail'] = data['submission']['email']
        user_data['password'] = crypt.encrypt(data['submission']['password'])

        # Update user info
        request_status = user.update_user(data['user']['id'], user_data)

        if request_status == codes.USER_NOT_FOUND:
            return jsonify(slack.UPDATE_USER_NOT_FOUND), 200

        if request_status != codes.SUCCESS:
            slack.post_ephemeral_response_message(messages.set_custom_message('UPDATE_USER_ERROR', [request_status]),
                                                  data['response_url'])
            return make_response('', 200)

        slack.post_ephemeral_response_message(messages.UPDATE_USER_SUCCESS, data['response_url'])

    elif data['callback_id'] == slack.DELETE_USER_CALLBACK:

        # Delete an user
        request_status = user.delete_user(data['user']['id'])

        if request_status == codes.USER_NOT_FOUND:
            return jsonify(slack.DELETE_USER_NOT_FOUND), 200

        if request_status != codes.SUCCESS:
            slack.post_ephemeral_response_message(messages.set_custom_message('DELETE_USER_ERROR', [request_status]),
                                                  data['response_url'])
            return make_response('', 200)

        slack.post_ephemeral_response_message(messages.DELETE_USER_SUCCESS, data['response_url'])

    return make_response('', 200)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.CLOCK_REQUEST, methods=['POST'])
def clock():
    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, 'clock')

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', 200)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.ADD_USER_REQUEST, methods=['POST'])
def sign_up():
    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, 'sign_up')

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', 200)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.UPDATE_USER_REQUEST, methods=['POST'])
def update_user():
    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, 'update_user')

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', 200)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.DELETE_USER_REQUEST, methods=['POST'])
def delete_user():
    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, 'delete_user')

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', 200)

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(host=settings.SLACK_SERVICE_HOST, port=settings.SLACK_SERVICE_PORT, debug=settings.DEBUG_MODE)
