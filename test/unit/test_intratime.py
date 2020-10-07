import pytest
import os

from datetime import datetime, timedelta
from intratime_slack_bot.config.settings import INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD
from intratime_slack_bot.lib import intratime, messages, logger, codes, time_utils
from intratime_slack_bot.lib.test_utils import read_json_file_data, check_if_log_exist, UNIT_TEST_DATA_PATH, TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------


TEST_GET_ACTION_DATA = [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH, 'intratime',
                        'test_get_action.json'))]
TEST_CLOCKING_ACTIONS_DATA = [item['action'] for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH,
                              'intratime', 'test_clocking_actions.json'))]
TEST_GET_USER_CLOCKS_DATA = [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH,
                             'intratime', 'test_get_user_clocks.json'))]

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
    # BAD CREDENTIALS
    assert intratime.get_auth_token('bar', 'foo', TEST_FILE) == codes.INTRATIME_AUTH_ERROR
    assert check_if_log_exist(messages.get(3003), TEST_FILE, logger.ERROR)

    # VALID CREDENTIALS
    assert isinstance(intratime.get_auth_token(INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD, TEST_FILE), str)
    assert check_if_log_exist(messages.make_message(1000, f"for user {INTRATIME_TEST_USER_EMAIL}"), TEST_FILE,
                              logger.DEBUG)

# ----------------------------------------------------------------------------------------------------------------------


def test_check_user_credentials(remove_test_file):
    # BAD CREDENTIALS
    assert intratime.check_user_credentials('bar', 'foo', TEST_FILE) is False
    assert check_if_log_exist(messages.get(3003), TEST_FILE, logger.ERROR)

    # VALID CREDENTIALS
    assert intratime.check_user_credentials(INTRATIME_TEST_USER_EMAIL, INTRATIME_TEST_USER_PASSWORD, TEST_FILE)
    assert check_if_log_exist(messages.make_message(1000, f"for user {INTRATIME_TEST_USER_EMAIL}"), TEST_FILE,
                              logger.DEBUG)

# ----------------------------------------------------------------------------------------------------------------------


def test_clocking_bad_auth(remove_test_file):
    code_result = intratime.clocking(intratime.IN_ACTION, 'bad_token', 'test@email.com', TEST_FILE)
    assert code_result == codes.UNAUTHORIZED

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('action', TEST_CLOCKING_ACTIONS_DATA)
def test_clocking_actions(token, action, remove_test_file):
    # SET CHECK INTERVAL [current_datetime, current_datetime + 2 seconds]
    datetime_from = time_utils.get_current_date_time()
    datetime_to = str(datetime.strptime(datetime_from, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=2))
    user_info_message = f"- user: {INTRATIME_TEST_USER_EMAIL}, action: {action}"

    # CLOCK ACTION
    assert intratime.clocking(action, token, INTRATIME_TEST_USER_EMAIL, TEST_FILE) == 0

    # CHECK THAT THE REGISTRATION HAS BEEN POSTED
    assert len(intratime.get_user_clocks(token, datetime_from, datetime_to, action)) > 0
    assert check_if_log_exist(messages.make_message(2000, user_info_message), TEST_FILE, logger.INFO)

# ----------------------------------------------------------------------------------------------------------------------


def test_get_user_clocks_bad_token():
    code_result = intratime.get_user_clocks('bad_token', '2020-10-10 00:00:00', '2020-10-10 01:00:00',
                                            intratime.IN_ACTION, TEST_FILE)
    assert code_result == codes.UNAUTHORIZED

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('datetime_from, datetime_to, action, result', TEST_GET_USER_CLOCKS_DATA)
def test_get_user_clocks(token, datetime_from, datetime_to, action, result):
    data_result = intratime.get_user_clocks(token, datetime_from, datetime_to, action, TEST_FILE)
    assert data_result == result
