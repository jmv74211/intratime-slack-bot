import pytest
import os

from datetime import datetime, timedelta
from intratime_slack_bot.lib import intratime, messages, logger, codes
from intratime_slack_bot.lib.test_utils import read_json_file_data, check_if_log_exist, UNIT_TEST_DATA_PATH, TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------


TEST_GET_ACTION_DATA = [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH, 'intratime',
                        'test_get_action.json'))]
TEST_CLOCKING_ACTIONS_DATA = [item['action'] for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH,
                              'intratime', 'test_clocking_actions.json'))]
TEST_GET_USER_CLOCKS_DATA = [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH,
                             'intratime', 'test_get_user_clocks.json'))]

INTRATIME_TEST_USER_EMAIL = os.environ['INTRATIME_TEST_USER_EMAIL']
INTRATIME_TEST_USER_PASSWORD = os.environ['INTRATIME_TEST_USER_PASSWORD']

token = intratime.get_auth_token(INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD, TEST_FILE)

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('action, output', TEST_GET_ACTION_DATA)
def test_get_action(action, output):
    assert intratime.get_action(action) == output

# ----------------------------------------------------------------------------------------------------------------------


def test_get_action_log_error(remove_test_file):
    intratime.get_action('foo', TEST_FILE)

    assert check_if_log_exist(messages.get(3000), TEST_FILE, logger.ERROR)

# ----------------------------------------------------------------------------------------------------------------------


def test_get_auth_token(remove_test_file):
    # Test bad credentials
    assert intratime.get_auth_token('bar', 'foo', TEST_FILE) == codes.INTRATIME_AUTH_ERROR
    assert check_if_log_exist(messages.get(3003), TEST_FILE, logger.ERROR)

    # Test correct credentials
    assert isinstance(intratime.get_auth_token(INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD, TEST_FILE), str)
    assert check_if_log_exist(messages.make_message(1000, f"for user {INTRATIME_TEST_USER_EMAIL}"), TEST_FILE,
                              logger.DEBUG)

# ----------------------------------------------------------------------------------------------------------------------


def test_check_user_credentials(remove_test_file):
    # Test bad credentials
    assert intratime.check_user_credentials('bar', 'foo', TEST_FILE) is False
    assert check_if_log_exist(messages.get(3003), TEST_FILE, logger.ERROR)

    # Test correct credentials
    assert intratime.check_user_credentials(INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD, TEST_FILE)
    assert check_if_log_exist(messages.make_message(1000, f"for user {INTRATIME_TEST_USER_EMAIL}"), TEST_FILE,
                              logger.DEBUG)

# ----------------------------------------------------------------------------------------------------------------------


def test_clocking_bad_auth(remove_test_file):
    assert intratime.clocking(intratime.IN_ACTION, 'bad_token', INTRATIME_TEST_USER_EMAIL, TEST_FILE) == 2
    assert check_if_log_exist(messages.get(3004), TEST_FILE, logger.ERROR)

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('action', TEST_CLOCKING_ACTIONS_DATA)
def test_clocking_actions(action, remove_test_file):
    # Set check interval: [current_datetime, current_datetime + 2 seconds]
    datetime_from = logger.get_current_date_time()
    datetime_to = str(datetime.strptime(datetime_from, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=2))
    user_info_message = f"- user: {INTRATIME_TEST_USER_EMAIL}, action: {action}"

    # Clock action
    assert intratime.clocking(action, token, INTRATIME_TEST_USER_EMAIL, TEST_FILE) == 0

    # Check that the registration has been posted
    assert len(intratime.get_user_clocks(token, datetime_from, datetime_to, action)) > 0
    assert check_if_log_exist(messages.make_message(2000, user_info_message), TEST_FILE, logger.INFO)

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('datetime_from, datetime_to, action, expected_result', TEST_GET_USER_CLOCKS_DATA)
def test_get_user_clocks(datetime_from, datetime_to, action, expected_result, remove_test_file):
    assert len(intratime.get_user_clocks(token, datetime_from, datetime_to, action)) == expected_result
