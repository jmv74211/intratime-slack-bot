import pytest
import os

from intratime_slack_bot.lib.test_utils import TEST_FILE
from intratime_slack_bot.lib import intratime
from intratime_slack_bot.config.settings import INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def remove_test_file(request):
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

# ---------------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope='module')
def token(request):
    token = intratime.get_auth_token(INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD, TEST_FILE)
    return token
