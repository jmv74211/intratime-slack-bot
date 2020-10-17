import requests
import json
import urllib.parse
import threading

from flask import Flask, jsonify, request, make_response
from http import HTTPStatus

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db import user
from intratime_slack_bot.lib import messages, warehouse, slack, intratime, codes, crypt, slack_ui

app = Flask(__name__)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.ECHO_REQUEST, methods=['GET'])
def echo():
    return jsonify({'result': messages.ALIVE_MESSAGE})

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.INTERACTIVE_REQUEST, methods=['POST'])
def get_interactive_data():
    data = urllib.parse.unquote(request.get_data().decode('utf-8'))

    # Clean string to convert it to json format
    data = json.loads(data.replace('payload=', ''))

    if data['callback_id'] == slack.CLOCK_CALLBACK:
        # Check if the user already exists
        if not user.user_exist(data['user']['id']):
            return jsonify(slack.CLOCKING_USER_NOT_FOUND), 200

        user_data = user.get_user_data(data['user']['id'])

        # Validate credentials
        if not intratime.check_user_credentials(user_data['intratime_mail'], crypt.decrypt(user_data['password'])):
            return jsonify(slack.BAD_BD_CREDENTIALS), 200

    elif data['callback_id'] == slack.ADD_USER_CALLBACK:
        # Check if the user already exists
        if user.user_exist(data['user']['id']):
            return jsonify(slack.USER_ALREADY_REGISTERED_MESSAGE), 200

        # Validate credentials
        if not intratime.check_user_credentials(data['submission']['email'], data['submission']['password']):
            return jsonify(slack.BAD_CREDENTIALS), 200

    elif data['callback_id'] == slack.UPDATE_USER_CALLBACK:
        # Validate credentials
        if not intratime.check_user_credentials(data['submission']['email'], data['submission']['password']):
            return jsonify(slack.BAD_CREDENTIALS), 200

        user_data = user.get_user_data(data['user']['id'])

        if user_data == codes.USER_NOT_FOUND:
            return jsonify(slack.UPDATE_USER_NOT_FOUND), 200

    elif data['callback_id'] == slack.DELETE_USER_CALLBACK:
        # Check if the user exists
        if data['submission']['delete'] == 'no':
            return make_response('', 200)
        elif not user.user_exist(data['user']['id']):
            return jsonify(slack.DELETE_USER_NOT_FOUND), 200

    process = threading.Thread(target=slack.process_interactive_data, args=(data,))
    process.start()

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
