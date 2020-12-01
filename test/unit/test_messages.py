import pytest
import os
import freezegun

from intratime_slack_bot.lib import messages, test_utils

# ----------------------------------------------------------------------------------------------------------------------

TEST_MODULE_NAME = 'messages'

TEST_MAKE_MESSAGE_DATA = test_utils.load_template_test_data(TEST_MODULE_NAME, 'test_make_message.json')

TEST_SET_CUSTOM_MESSAGE_DATA = test_utils.load_template_test_data(TEST_MODULE_NAME, 'test_set_custom_message.json')

TEST_GENERATE_SLACK_HISTORY_REPORT_DATA = test_utils.load_template_test_data(TEST_MODULE_NAME,
                                                                             'test_generate_slack_history_report.json')

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('code, custom_message, expected_result', TEST_MAKE_MESSAGE_DATA)
def test_make_message(code, custom_message, expected_result):
    assert messages.make_message(code, custom_message) == expected_result

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('key, parameters, expected_result', TEST_SET_CUSTOM_MESSAGE_DATA)
def test_set_custom_message(key, parameters, expected_result):
    assert messages.set_custom_message(key, parameters) == expected_result

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('action, fake_datetime, data, worked_time, callback_id, expected_result',
                         TEST_GENERATE_SLACK_HISTORY_REPORT_DATA)
def test_generate_slack_history_report(action, fake_datetime, data, worked_time, callback_id, expected_result, token):
    with freezegun.freeze_time(fake_datetime):
        assert messages.generate_slack_history_report(token, action, data, worked_time, callback_id) == expected_result
