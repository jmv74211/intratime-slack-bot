import pytest
import os

from intratime_slack_bot.lib import intratime, messages, logger
from intratime_slack_bot.lib.test_utils import read_json_file_data, check_if_log_exist, UNIT_TEST_DATA_PATH, TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------


test_get_action_data = [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH, 'intratime',
                        'test_get_action.json'))]


@pytest.mark.parametrize('action, output', test_get_action_data)
def test_get_action(action, output):
    assert intratime.get_action(action) == output


def test_get_action_log_error(remove_test_file):
    intratime.get_action('foo', TEST_FILE)

    assert check_if_log_exist(messages.get(3000), TEST_FILE, logger.ERROR)
