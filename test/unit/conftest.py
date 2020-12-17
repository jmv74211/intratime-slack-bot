import pytest
import os
from time import sleep

from intratime_slack_bot.lib.test_utils import TEST_FILE
from intratime_slack_bot.config import settings
from intratime_slack_bot.lib import intratime, crypt, logger, slack, logger
from intratime_slack_bot.lib.db import user
from intratime_slack_bot.config.settings import INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD

# ----------------------------------------------------------------------------------------------------------------------


TEST_USER_DATA = {'user_id': 'test', 'user_name': 'test', 'intratime_mail': settings.INTRATIME_TEST_USER_EMAIL,
                  'password': crypt.encrypt(settings.INTRATIME_TEST_USER_PASSWORD),
                  'registration_date': '2020-09-18 15:57:00', 'last_registration_date': '2020-09-15 15:58:00'}

CLOCK_SLEEP_TIME = 1

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def remove_test_file(request):
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope='module')
def token(request):
    token = intratime.get_auth_token(INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD)
    return token

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def add_user(request):
    user_exist = user.user_exist(TEST_USER_DATA['user_id'])

    if not user_exist:
        user.add_user(TEST_USER_DATA)

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def pre_delete_user(request):
    user_exist = user.user_exist(TEST_USER_DATA['user_id'])

    if user_exist:
        user.delete_user(TEST_USER_DATA['user_id'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def post_delete_user(request):
    yield

    user_exist = user.user_exist(TEST_USER_DATA['user_id'])

    if user_exist:
        user.delete_user(TEST_USER_DATA['user_id'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def pre_clock_in(request, token):
    sleep(CLOCK_SLEEP_TIME)
    intratime.clocking(intratime.IN_ACTION, token, TEST_USER_DATA['intratime_mail'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def post_clock_in(request, token):
    yield
    sleep(CLOCK_SLEEP_TIME)
    intratime.clocking(intratime.IN_ACTION, token, TEST_USER_DATA['intratime_mail'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def pre_clock_pause(request, token):
    sleep(CLOCK_SLEEP_TIME)
    intratime.clocking(intratime.PAUSE_ACTION, token, TEST_USER_DATA['intratime_mail'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def post_clock_pause(request, token):
    yield
    sleep(CLOCK_SLEEP_TIME)
    intratime.clocking(intratime.PAUSE_ACTION, token, TEST_USER_DATA['intratime_mail'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def pre_clock_return(request, token):
    sleep(CLOCK_SLEEP_TIME)
    intratime.clocking(intratime.RETURN_ACTION, token, TEST_USER_DATA['intratime_mail'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def post_clock_return(request, token):
    yield
    sleep(CLOCK_SLEEP_TIME)
    intratime.clocking(intratime.RETURN_ACTION, token, TEST_USER_DATA['intratime_mail'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def pre_clock_out(request, token):
    sleep(CLOCK_SLEEP_TIME)
    intratime.clocking(intratime.OUT_ACTION, token, TEST_USER_DATA['intratime_mail'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def post_clock_out(request, token):
    yield
    sleep(CLOCK_SLEEP_TIME)
    intratime.clocking(intratime.OUT_ACTION, token, TEST_USER_DATA['intratime_mail'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def mock_slack_logger(remove_test_file):
    backup_logger = slack.LOGGER
    slack.LOGGER = logger.get_logger('test', settings.LOGS_LEVEL, TEST_FILE)
    yield
    slack.LOGGER = backup_logger

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def mock_intratime_logger(remove_test_file):
    backup_logger = intratime.LOGGER
    intratime.LOGGER = logger.get_logger('test', settings.LOGS_LEVEL, TEST_FILE)
    yield
    intratime.LOGGER = backup_logger

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def mock_user_logger(remove_test_file):
    backup_logger = user.LOGGER
    user.LOGGER = logger.get_logger('test', settings.LOGS_LEVEL, TEST_FILE)
    yield
    user.LOGGER = backup_logger
