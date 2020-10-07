from flask import Flask, jsonify, request
from http import HTTPStatus

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib import intratime, messages, warehouse, codes

app = Flask(__name__)

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.ECHO_REQUEST, methods=['GET'])
def echo():
    return jsonify({'result': messages.ALIVE_MESSAGE})

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.CHECK_USER_CREDENTIALS_REQUEST, methods=['GET'])
def check_credentials():
    data = request.get_json()

    if data is None or 'email' not in data or 'password' not in data:
        return jsonify({'result': messages.BAD_DATA_MESSAGE}), HTTPStatus.BAD_REQUEST

    credentials_ok = intratime.check_user_credentials(data['email'], data['password'])

    if credentials_ok:
        return jsonify({'result': True}), HTTPStatus.OK
    else:
        return jsonify({'result': False}), HTTPStatus.OK

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.GET_AUTH_TOKEN_REQUEST, methods=['GET'])
def get_auth_token():
    data = request.get_json()

    if data is None or 'email' not in data or 'password' not in data:
        return jsonify({'result': messages.BAD_DATA_MESSAGE}), HTTPStatus.BAD_REQUEST

    credentials_ok = intratime.check_user_credentials(data['email'], data['password'])

    if credentials_ok:
        token = intratime.get_auth_token(data['email'], data['password'])
        return jsonify({'result': token}), HTTPStatus.OK
    else:
        return jsonify({'result': messages.BAD_CREDENTIALS}), HTTPStatus.OK

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.GET_USER_CLOCKS_REQUEST, methods=['GET'])
def get_user_clocks():
    data = request.get_json()
    action = None

    if data is None or 'token' not in data or 'datetime_from' not in data or 'datetime_to' not in data:
        return jsonify({'result': messages.BAD_DATA_MESSAGE}), HTTPStatus.BAD_REQUEST

    if 'action' in data:
        action = data['action']

    data_result = intratime.get_user_clocks(data['token'], data['datetime_from'], data['datetime_to'], action=action)

    if isinstance(data_result, int) and data_result == codes.UNAUTHORIZED:
        return jsonify({'result': messages.BAD_TOKEN}), HTTPStatus.UNAUTHORIZED
    elif isinstance(data_result, int) and data_result == codes.INTRATIME_NO_RESPONSE:
        return jsonify({'result': messages.BAD_INTRATIME_CONNECTION}), HTTPStatus.OK
    elif isinstance(data_result, int) and data_result == codes.INTRATIME_API_CONNECTION_ERROR:
        return jsonify({'result': messages.BAD_INTRATIME_RESPONSE}), HTTPStatus.OK

    return jsonify({'result': data_result}), HTTPStatus.OK

# ----------------------------------------------------------------------------------------------------------------------


@app.route(warehouse.CLOCK_REQUEST, methods=['POST'])
def clocking():
    data = request.get_json()

    if data is None or 'token' not in data or 'action' not in data or 'email' not in data:
        return jsonify({'result': messages.BAD_DATA_MESSAGE}), HTTPStatus.BAD_REQUEST

    data_result = intratime.clocking(data['action'], data['token'], data['email'])

    if isinstance(data_result, int) and data_result == codes.UNAUTHORIZED:
        return jsonify({'result': messages.BAD_TOKEN}), HTTPStatus.UNAUTHORIZED
    elif isinstance(data_result, int) and data_result == codes.INTRATIME_NO_RESPONSE:
        return jsonify({'result': messages.BAD_INTRATIME_CONNECTION}), HTTPStatus.OK
    elif isinstance(data_result, int) and data_result == codes.INTRATIME_API_CONNECTION_ERROR:
        return jsonify({'result': messages.BAD_INTRATIME_RESPONSE}), HTTPStatus.OK

    return jsonify({'result': 'ok'}), HTTPStatus.OK

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(host=settings.INTRATIME_SERVICE_HOST, port=settings.INTRATIME_SERVICE_PORT, debug=settings.DEBUG_MODE)
