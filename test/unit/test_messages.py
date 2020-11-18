import pytest
import os
import freezegun

from intratime_slack_bot.lib import messages
from intratime_slack_bot.lib.test_utils import read_json_file_data, UNIT_TEST_DATA_PATH

# ----------------------------------------------------------------------------------------------------------------------


TEST_MAKE_MESSAGE_DATA = [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH, 'messages',
                          'test_make_message.json'))]
TEST_SET_CUSTOM_MESSAGE_DATA = [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH,
                                'messages', 'test_set_custom_message.json'))]
TEST_GENERATE_SLACK_HISTORY_REPORT_DATA = \
    [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH, 'messages',
                                                                'test_generate_slack_history_report.json'))]

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('code, custom_message, expected_result', TEST_MAKE_MESSAGE_DATA)
def test_make_message(code, custom_message, expected_result):
    assert messages.make_message(code, custom_message) == expected_result

# ----------------------------------------------------------------------------------------------------------------------


def get_exception_message():
    try:
        exception = 1/0
    except ZeroDivisionError as e:
        exception = e

    assert messages.get_exception_message() == "division by zero"

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('key, parameters, expected_result', TEST_SET_CUSTOM_MESSAGE_DATA)
def test_set_custom_message(key, parameters, expected_result):
    assert messages.set_custom_message(key, parameters) == expected_result

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('action, fake_datetime, data, expected_result', TEST_GENERATE_SLACK_HISTORY_REPORT_DATA)
def test_generate_slack_history_report(action, fake_datetime, data, expected_result, token):
    with freezegun.freeze_time(fake_datetime):
        assert messages.generate_slack_history_report(token, action, data) == expected_result
