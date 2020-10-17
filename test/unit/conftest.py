import pytest
import os

from intratime_slack_bot.lib.test_utils import TEST_FILE
from intratime_slack_bot.config import settings
from intratime_slack_bot.lib import intratime, crypt
from intratime_slack_bot.lib.db import user
from intratime_slack_bot.config.settings import INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD

# ----------------------------------------------------------------------------------------------------------------------


TEST_USER_DATA = {'user_id': 'test', 'username': 'test', 'intratime_mail': settings.INTRATIME_TEST_USER_EMAIL,
                  'password': crypt.encrypt(settings.INTRATIME_TEST_USER_PASSWORD),
                  'registration_date': '2020-09-18 15:57:00', 'last_registration_date': '2020-09-15 15:58:00'}

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def remove_test_file(request):
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope='module')
def token(request):
    token = intratime.get_auth_token(INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD, TEST_FILE)
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
def clock_out(request):
    yield
    token = intratime.get_auth_token(TEST_USER_DATA['intratime_mail'], crypt.decrypt(TEST_USER_DATA['password']))
    intratime.clocking('out', token, TEST_USER_DATA['intratime_mail'])
