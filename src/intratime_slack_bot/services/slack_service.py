import requests
import json
import urllib.parse
import threading
import logging
import sys
import os
import time
import hmac
import hashlib

from flask import Flask, jsonify, request, make_response
from http import HTTPStatus
from functools import wraps
from logging.handlers import TimedRotatingFileHandler

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db import user
from intratime_slack_bot.lib.db.monitoring import add_history_register
from intratime_slack_bot.lib import messages, warehouse, slack, intratime, codes, crypt, slack_ui

# ----------------------------------------------------------------------------------------------------------------------


app = Flask(__name__)


# Configure log handlers
logger = logging.getLogger('werkzeug')

app_file_handler = TimedRotatingFileHandler(os.path.join(settings.LOGS_PATH, 'app.log'), when='midnight')
error_file_handler = TimedRotatingFileHandler(os.path.join(settings.LOGS_PATH, 'app_error.log'), when='midnight')

app_file_handler.setLevel(logging.DEBUG)
error_file_handler.setLevel(logging.ERROR)

# Logger needed to log flask logs
logger.addHandler(app_file_handler)

# Logger needed to log errors too in app log file (It works with debug false)
app.logger.addHandler(app_file_handler)

# Logger needed to log only errors in errors log file (It works with debug false)
app.logger.addHandler(error_file_handler)


ALLOWED_COMMANDS = {
    "/clock": {
        "allowed_parameters": ['in', 'pause', 'return', 'out'],
        "callback_id": slack.CLOCK_CALLBACK
    },
    "/clock_history": {
        "allowed_parameters": ['today', 'week', 'month'],
        "callback_id": slack.CLOCK_HISTORY_CALLBACK
    },
    "/time_history": {
        "allowed_parameters": ['today', 'week', 'month'],
        "callback_id": slack.TIME_HISTORY_CALLBACK
    },
    "/time": {
        "allowed_parameters": ['today', 'week', 'month'],
        "callback_id": slack.WORKED_TIME_CALLBACK
    },
    "/sign_up": {
        "allowed_parameters": [],
        "callback_id": slack.ADD_USER_CALLBACK
    },
    "/update_user": {
        "allowed_parameters": [],
        "callback_id": slack.UPDATE_USER_CALLBACK
    },
    "/delete_user": {
        "allowed_parameters": [],
        "callback_id": slack.DELETE_USER_CALLBACK
    },
    "/today": {
        "allowed_parameters": [],
        "callback_id": slack.TODAY_INFO_CALLBACK
    },
    "/help": {
        "allowed_parameters": [],
        "callback_id": slack.COMMAND_HELP_CALLBACK
    }
}

# ----------------------------------------------------------------------------------------------------------------------


def empty_response():
    return make_response('', HTTPStatus.OK)

# ----------------------------------------------------------------------------------------------------------------------
#                                                API DECORATORS                                                        #
# ----------------------------------------------------------------------------------------------------------------------


def validate_slack_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'X-Slack-Signature' not in request.headers or 'X-Slack-Request-Timestamp' not in request.headers:
            return jsonify({'result': messages.BAD_SLACK_HEADERS_REQUEST}), HTTPStatus.BAD_REQUEST

        request_signature = request.headers['X-Slack-Signature']
        request_timestamp = int(request.headers['X-Slack-Request-Timestamp'])
        request_body = request.get_data().decode('utf-8')

        # Verify that the request is not prior to 1 minute (Avoid replay attacks)
        if int(time.time() - request_timestamp) > 60:
            return jsonify({'result': messages.BAD_SLACK_TIMESTAMP_REQUEST}), HTTPStatus.BAD_REQUEST

        sign_basestring = f"v0:{request_timestamp}:{request_body}"
        signature = hmac.new(bytes(settings.SLACK_APP_SIGNATURE, 'utf-8'), bytes(sign_basestring, 'utf-8'),
                             digestmod=hashlib.sha256).hexdigest()
        signature_check = f"v0={signature}"

        # Validate request signature
        if not hmac.compare_digest(signature_check, request_signature):
            return jsonify({'result': messages.NON_SLACK_REQUEST}), HTTPStatus.UNAUTHORIZED

        return func(*args, **kwargs)

    return wrapper

# ----------------------------------------------------------------------------------------------------------------------


def validate_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Convert from x=y&z=h to {x:y, z:h}
        data = urllib.parse.parse_qs(request.get_data().decode('utf-8'))

        # Converts lists with size 1 into elements. e.g  x: ['test] --> x: 'test'
        for key, value in data.items():
            if type(value) is list and len(value) == 1:
                data[key] = value[0]

        if not user.user_exist(data['user_id']):
            message = messages.slack_warning_message('You are not registered. Please sign up using `/sign_up` command')
            slack.post_ephemeral_response_message([message], data['response_url'], 'blocks')
            return empty_response()

        return func(*args, **kwargs)

    return wrapper

# ----------------------------------------------------------------------------------------------------------------------


def monitoring(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = urllib.parse.parse_qs(request.get_data().decode('utf-8'))
        parameters = ""
        try:
            parameters = data['text'][0]
        except KeyError:
            pass

        history_data = {'user_name': data['user_name'][0], 'user_id': data['user_id'][0], 'command': data['command'][0],
                        'parameters': parameters}

        add_history_register(history_data)

        return func(*args, **kwargs)

    return wrapper

# ----------------------------------------------------------------------------------------------------------------------


def process_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # DECODE SLACK DATA
        data = urllib.parse.parse_qs(request.get_data().decode('utf-8'))  # Convert from x=y&z=h to {x:y, z:h}

        # Converts lists with size 1 into elements. e.g  x: ['test] --> x: 'test'
        for key, value in data.items():
            if type(value) is list and len(value) == 1:
                data[key] = value[0]

        parameters = [data['command']]

        # Get command parameters
        if 'text' in data:
            parameters.extend(data['text'].split(' '))

        command = parameters[0]

        if command not in ALLOWED_COMMANDS:
            print(f"Command {command} not exists")
            return empty_response()

        # Exception for today command (wrapper for /clock history today)
        if command == '/today':
            command = '/clock_history'
            parameters.append('today')

        callback_id = ALLOWED_COMMANDS[command]['callback_id']

        # If there is no command parameters and command has user interface
        if len(parameters) == 1:
            data = request.get_data().decode('utf-8')
            api_data = slack.get_api_data(data, callback_id)

            requests.post(warehouse.SLACK_OPEN_DIALOG_URL, data=api_data)

            return empty_response()

        command_parameter = parameters[1]

        if command_parameter not in ALLOWED_COMMANDS[command]['allowed_parameters']:
            message = messages.slack_warning_message(f"Bad parameter _{command_parameter}_ in `{command}` command")
            slack.post_ephemeral_response_message([message], data['response_url'], 'blocks')
            slack.post_ephemeral_response_message([messages.slack_command_help()], data['response_url'], 'blocks')
            return empty_response()

        # COMMAND WITH PARAMETERS SECTION
        if command == '/time':
            command_parameter += '_hours'
        elif command == '/time_history' or command == '/clock_history':
            command_parameter += '_history'

        data['callback_id'] = callback_id
        data['submission'] = {'action': command_parameter}
        data['user'] = {'id': data['user_id'], 'name': data['user_name']}

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        url = f"{settings.PROTOCOL}://localhost:{settings.SLACK_SERVICE_PORT}{warehouse.INTERACTIVE_REQUEST}"
        data = urllib.parse.urlencode({'payload': data})

        requests.post(url, data=data, headers=headers)

        return empty_response()

    return wrapper

# ----------------------------------------------------------------------------------------------------------------------
#                                                API REQUESTS                                                          #
# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.ECHO_REQUEST, methods=['GET'])
def echo():
    """
    Description: Endpoint to check the current server status

    Input_data: {}

    Output_data: {'result': 'Alive'}
    """
    return jsonify({'result': messages.ALIVE_MESSAGE})

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.INTERACTIVE_REQUEST, methods=['POST'])
@validate_slack_request
def get_interactive_data():
    """
    Description: Endpoint to manage form dialog requests

    Input_data: b'payload=%7B%22type%22%3A%22dialog_submission%22%2C%22token%22%3A%2action_ts%22%3A%221603652391.
                 624401%22%2C%22team%22%TR2ZRS%22%2C%22domain%22%2%2id%22%3A%HV86ES%22%2C%22name%22%3A%2%7D%2C%22
                 channel%22%3A%7B%22id%22%3A%22CS4J%22%2C%22name%22%3As%22%7D%2C%22submission%22%3A%7B%22email%22C%22
                 password%22%22%7D%2C%22callback_id%22%3A%22sign_up%22%2C%22response_url%22%3A%22ht...'

    Output_data: {}, 200
    """
    data = json.loads(urllib.parse.parse_qs(request.get_data().decode('utf-8'))['payload'][0].replace('\'', '"'))

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
@validate_slack_request
@validate_user
@monitoring
@process_request
def clock():
    """
    Description: Endpoint to clock a user action

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fclockr&text=x&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.ADD_USER_REQUEST, methods=['POST'])
@validate_slack_request
@process_request
def sign_up():
    """
    Description: Endpoint register a new user

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fsign_up&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.UPDATE_USER_REQUEST, methods=['POST'])
@validate_slack_request
@validate_user
@monitoring
@process_request
def update_user():
    """
    Description: Endpoint to update the user info

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x
                  &command=%2Fupdate_user&text=x&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.DELETE_USER_REQUEST, methods=['POST'])
@validate_slack_request
@validate_user
@monitoring
@process_request
def delete_user():
    """
    Description: Endpoint to delete an user from app

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fdelete_user&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.CLOCK_HISTORY_REQUEST, methods=['POST'])
@validate_slack_request
@validate_user
@monitoring
@process_request
def user_clock_history():
    """
    Description: Endpoint to get the user clock history

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fhistory&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.TIME_HISTORY_REQUEST, methods=['POST'])
@validate_slack_request
@validate_user
@monitoring
@process_request
def user_worked_time_history():
    """
    Description: Endpoint to get the user worked time history

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fhistory&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.WORKED_TIME_REQUEST, methods=['POST'])
@validate_slack_request
@validate_user
@monitoring
@process_request
def user_worked_time():
    """
    Description: Endpoint to get the user worked time

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Ftime&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.TODAY_INFO_REQUEST, methods=['POST'])
@validate_slack_request
@validate_user
@monitoring
@process_request
def user_today_info():
    """
    Description: Endpoint to get the clock history from today

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Ftoday&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.COMMAND_HELP_REQUEST, methods=['POST'])
@validate_slack_request
def command_help():
    """
    Description: Endpoint to get the command help

    Input_data: b'token=x&team_id=x&team_domain=x&channel_id=x&channel_name=x&user_id=x&user_name=x&
                  command=%2Fhelp&text=&api_app_id=x&response_url=x&trigger_id=x'

    Output_data: {}, 200
    """
    data = urllib.parse.parse_qs(request.get_data().decode('utf-8'))
    slack.post_ephemeral_response_message([messages.slack_command_help()], data['response_url'][0], 'blocks')

    return empty_response()

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(host=settings.SLACK_SERVICE_HOST, port=settings.SLACK_SERVICE_PORT, debug=settings.DEBUG_MODE)
