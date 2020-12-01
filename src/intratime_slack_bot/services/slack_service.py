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
    """
    Description: Endpoint to check the current server status

    Input_data: {}

    Output_data: {'result': True/False}
    """

    return jsonify({'result': messages.ALIVE_MESSAGE}),

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.INTERACTIVE_REQUEST, methods=['POST'])
def get_interactive_data():
    """
    Description: Endpoint to manage form dialog requests

    Input_data: b'payload=%7B%22type%22%3A%22dialog_submission%22%2C%22token%22%3A%2action_ts%22%3A%221603652391.
                 624401%22%2C%22team%22%TR2ZRS%22%2C%22domain%22%2%2id%22%3A%HV86ES%22%2C%22name%22%3A%2%7D%2C%22
                 channel%22%3A%7B%22id%22%3A%22CS4J%22%2C%22name%22%3As%22%7D%2C%22submission%22%3A%7B%22email%22C%22
                 password%22%22%7D%2C%22callback_id%22%3A%22sign_up%22%2C%22response_url%22%3A%22ht...'

    Output_data: {}, 200
    """

    data = urllib.parse.unquote(request.get_data().decode('utf-8'))

    # Clean string to convert it to json format
    data = json.loads(data.replace('payload=', ''))

    if data['callback_id'] == slack.CLOCK_CALLBACK:
        # Check if the user do not exist
        if not user.user_exist(data['user']['id']):
            return jsonify(slack.CLOCKING_USER_NOT_FOUND), HTTPStatus.OK

        user_data = user.get_user_data(data['user']['id'])

        # Validate credentials
        if not intratime.check_user_credentials(user_data['intratime_mail'], crypt.decrypt(user_data['password'])):
            return jsonify(slack.BAD_BD_CREDENTIALS), HTTPStatus.OK

    elif data['callback_id'] == slack.CLOCK_HISTORY_CALLBACK or data['callback_id'] == slack.TIME_HISTORY_CALLBACK:
        # Check if the user do not exist
        if not user.user_exist(data['user']['id']):
            return jsonify(slack.CLOCKING_USER_NOT_FOUND), HTTPStatus.OK

    elif data['callback_id'] == slack.ADD_USER_CALLBACK:
        # Check if the user already exists
        if user.user_exist(data['user']['id']):
            return jsonify(slack.USER_ALREADY_REGISTERED_MESSAGE), HTTPStatus.OK

        # Validate credentials
        if not intratime.check_user_credentials(data['submission']['email'], data['submission']['password']):
            return jsonify(slack.BAD_CREDENTIALS), HTTPStatus.OK

    elif data['callback_id'] == slack.UPDATE_USER_CALLBACK:
        # Validate credentials
        if not intratime.check_user_credentials(data['submission']['email'], data['submission']['password']):
            return jsonify(slack.BAD_CREDENTIALS), HTTPStatus.OK

        user_data = user.get_user_data(data['user']['id'])

        if user_data == codes.USER_NOT_FOUND:
            return jsonify(slack.UPDATE_USER_NOT_FOUND), HTTPStatus.OK

    elif data['callback_id'] == slack.DELETE_USER_CALLBACK:
        # Check if the user exists
        if data['submission']['delete'] == 'no':
            return make_response('', HTTPStatus.OK)
        elif not user.user_exist(data['user']['id']):
            return jsonify(slack.DELETE_USER_NOT_FOUND), HTTPStatus.OK

    process = threading.Thread(target=slack.process_interactive_data, args=(data,))
    process.start()

    return make_response('', HTTPStatus.OK)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.CLOCK_REQUEST, methods=['POST'])
def clock():
    """
    Description: Endpoint to clock a user action

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fclockr&text=x&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, slack.CLOCK_CALLBACK)

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', HTTPStatus.OK)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.ADD_USER_REQUEST, methods=['POST'])
def sign_up():
    """
    Description: Endpoint register a new user

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fsign_up&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, slack.ADD_USER_CALLBACK)

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', HTTPStatus.OK)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.UPDATE_USER_REQUEST, methods=['POST'])
def update_user():
    """
    Description: Endpoint to update the user info

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x
                  &command=%2Fupdate_user&text=x&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, slack.UPDATE_USER_CALLBACK)

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', HTTPStatus.OK)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.DELETE_USER_REQUEST, methods=['POST'])
def delete_user():
    """
    Description: Endpoint to delete an user from app

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fdelete_user&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, slack.DELETE_USER_CALLBACK)

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', HTTPStatus.OK)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.CLOCK_HISTORY_REQUEST, methods=['POST'])
def user_clock_history():
    """
    Description: Endpoint to get the user clock history

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fhistory&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, slack.CLOCK_HISTORY_CALLBACK)

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', HTTPStatus.OK)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.TIME_HISTORY_REQUEST, methods=['POST'])
def user_worked_time_history():
    """
    Description: Endpoint to get the user worked time history

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fhistory&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, slack.TIME_HISTORY_CALLBACK)

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', HTTPStatus.OK)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.WORKED_TIME_REQUEST, methods=['POST'])
def user_worked_time():
    """
    Description: Endpoint to get the user worked time

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Ftime&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

    data = request.get_data().decode('utf-8')

    api_data = slack.get_api_data(data, slack.WORKED_TIME_CALLBACK)

    requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

    return make_response('', HTTPStatus.OK)

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(host=settings.SLACK_SERVICE_HOST, port=settings.SLACK_SERVICE_PORT, debug=settings.DEBUG_MODE)
