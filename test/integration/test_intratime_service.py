import pytest
import os
import requests
import time

from http import HTTPStatus
from intratime_slack_bot.config.settings import INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD
from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.test_utils import read_json_file_data, INTEGRATION_TEST_DATA_PATH
from intratime_slack_bot.lib import process, warehouse, messages

# ----------------------------------------------------------------------------------------------------------------------


BASE_URL = f"{settings.PROTOCOL}://{settings.INTRATIME_SERVICE_HOST}:{settings.INTRATIME_SERVICE_PORT}"

# ----------------------------------------------------------------------------------------------------------------------


def test_echo(launch_intratime_service):
    request = requests.get(f"{BASE_URL}/{warehouse.ECHO_REQUEST}")
    assert request.json()['result'] == messages.ALIVE_MESSAGE

# ----------------------------------------------------------------------------------------------------------------------


def test_get_auth_token(launch_intratime_service):
    BAD_DATA = {"data": "bad_data"}
    BAD_CREDENTIALS_DATA = {"email": INTRATIME_TEST_USER_EMAIL, "password": "bad_password"}
    DATA = {"email": INTRATIME_TEST_USER_EMAIL, "password": INTRATIME_TEST_USER_PASSWORD}

    # BAD DATA
    request = requests.get(f"{BASE_URL}/{warehouse.GET_AUTH_TOKEN_REQUEST}", json=BAD_DATA)
    assert request.status_code == HTTPStatus.BAD_REQUEST
    assert request.json()['result'] == messages.BAD_DATA_MESSAGE

    # BAD CREDENTIALS
    request = requests.get(f"{BASE_URL}/{warehouse.GET_AUTH_TOKEN_REQUEST}", json=BAD_CREDENTIALS_DATA)
    assert request.status_code == HTTPStatus.OK
    assert request.json()['result'] == messages.BAD_CREDENTIALS

    # VALID CREDENTIALS
    request = requests.get(f"{BASE_URL}/{warehouse.GET_AUTH_TOKEN_REQUEST}", json=DATA)
    assert request.status_code == HTTPStatus.OK
    assert request.json()['result'] != messages.BAD_CREDENTIALS

# ----------------------------------------------------------------------------------------------------------------------


def test_check_user_credentials(launch_intratime_service):
    BAD_DATA = {"data": "bad_data"}
    BAD_CREDENTIALS_DATA = {"email": INTRATIME_TEST_USER_EMAIL, "password": "bad_password"}
    DATA = {"email": INTRATIME_TEST_USER_EMAIL, "password": INTRATIME_TEST_USER_PASSWORD}

    # BAD DATA
    request = requests.get(f"{BASE_URL}{warehouse.CHECK_USER_CREDENTIALS_REQUEST}", json=BAD_DATA)
    assert request.status_code == HTTPStatus.BAD_REQUEST
    assert request.json()['result'] == messages.BAD_DATA_MESSAGE

    # BAD CREDENTIALS
    request = requests.get(f"{BASE_URL}{warehouse.CHECK_USER_CREDENTIALS_REQUEST}", json=BAD_CREDENTIALS_DATA)
    assert request.status_code == HTTPStatus.OK
    assert not request.json()['result']

    # VALID CREDENTIALS
    request = requests.get(f"{BASE_URL}/{warehouse.CHECK_USER_CREDENTIALS_REQUEST}", json=DATA)
    assert request.status_code == HTTPStatus.OK
    assert request.json()['result']

# ----------------------------------------------------------------------------------------------------------------------


def test_get_user_clocks(launch_intratime_service, token):
    DATA = {"token": token, "datetime_from": '2020-09-17 00:00:00', "datetime_to": '2020-09-18 00:00:00'}
    BAD_TOKEN_DATA = {"token": 'badtoken', "datetime_from": '2020-09-17 00:00:00', "datetime_to": '2020-09-18 00:00:00'}
    BAD_DATA = {"token": token, "datetime_from": '2020-09-17 00:00:00', "action": "in"}

    # BAD DATA
    request = requests.get(f"{BASE_URL}{warehouse.GET_USER_CLOCKS_REQUEST}", json=BAD_DATA)
    assert request.status_code == HTTPStatus.BAD_REQUEST
    assert request.json()['result'] == messages.BAD_DATA_MESSAGE

    # BAD TOKEN DATA
    request = requests.get(f"{BASE_URL}{warehouse.GET_USER_CLOCKS_REQUEST}", json=BAD_TOKEN_DATA)
    assert request.status_code == HTTPStatus.UNAUTHORIZED
    assert request.json()['result'] == messages.BAD_TOKEN

    # VALID DATA
    request = requests.get(f"{BASE_URL}/{warehouse.GET_USER_CLOCKS_REQUEST}", json=DATA)
    assert request.status_code == HTTPStatus.OK
    assert len(request.json()['result']) > 0

# ----------------------------------------------------------------------------------------------------------------------


def test_clocking(launch_intratime_service, token):
    DATA = {"token": token, "action": 'in', "email": INTRATIME_TEST_USER_EMAIL}
    BAD_TOKEN_DATA = {"token": 'bad_token', "action": 'in', "email": INTRATIME_TEST_USER_EMAIL}
    BAD_DATA = {"token": 'bad_token', "email": INTRATIME_TEST_USER_EMAIL}

    # BAD DATA
    request = requests.post(f"{BASE_URL}{warehouse.CLOCK_REQUEST}", json=BAD_DATA)
    assert request.status_code == HTTPStatus.BAD_REQUEST
    assert request.json()['result'] == messages.BAD_DATA_MESSAGE

    # BAD TOKEN DATA
    request = requests.post(f"{BASE_URL}{warehouse.CLOCK_REQUEST}", json=BAD_TOKEN_DATA)
    assert request.status_code == HTTPStatus.UNAUTHORIZED
    assert request.json()['result'] == messages.BAD_TOKEN

    # VALID DATA
    request = requests.post(f"{BASE_URL}/{warehouse.CLOCK_REQUEST}", json=DATA)
    assert request.status_code == HTTPStatus.OK
    assert request.json()['result'] == 'ok'
