import pytest
import requests

from http import HTTPStatus
from intratime_slack_bot.config import settings
from intratime_slack_bot.lib import slack, warehouse, messages

# ----------------------------------------------------------------------------------------------------------------------

SLACK_SERVICE_BASE_URL = warehouse.SLACK_SERVICE_BASE_URL

# ----------------------------------------------------------------------------------------------------------------------


def test_echo(launch_slack_service):
    request = requests.get(f"{SLACK_SERVICE_BASE_URL}/{warehouse.ECHO_REQUEST}")
    assert request.json()['result'] == messages.ALIVE_MESSAGE

# ----------------------------------------------------------------------------------------------------------------------


def test_clock(launch_slack_service):
    request = requests.get(f"{SLACK_SERVICE_BASE_URL}/{warehouse.CLOCK_REQUEST}")
