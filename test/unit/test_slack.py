import pytest
import os
import re
import json
import requests
import freezegun

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db import user
from intratime_slack_bot.lib import slack, codes, messages, logger, intratime, time_utils, test_utils
from intratime_slack_bot.lib.test_utils import check_if_log_exist, read_json_file_data, UNIT_TEST_DATA_PATH, TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------

SLACK_CHANNEL = settings.SLACK_TEST_CHANNEL
TEXT = 'Test message'
TEXT_BLOCK = [{'type': 'section', 'text': {'type': 'mrkdwn', 'text': 'test'}}]
TEXT_ATTACHEMENT = [{"text": "Test message 2"}]
TEST_USER_ID = settings.SLACK_TEST_USER_ID
TEST_MODULE_NAME = 'slack'
SLACK_TEST_DATA_PATH = os.path.join(UNIT_TEST_DATA_PATH, TEST_MODULE_NAME)

TEST_DECODE_SLACK_ARGS_DATA = test_utils.load_template_test_data(TEST_MODULE_NAME, 'test_decode_slack_args.json')

TEST_GET_API_DATA = test_utils.load_template_test_data(TEST_MODULE_NAME, 'test_get_api_data.json')

TEST_GET_API_NAMES = [item['callback_id'] for item in read_json_file_data(os.path.join(SLACK_TEST_DATA_PATH,
                                                                                       'test_get_api_data.json'))]

TEST_GENERATE_CLOCK_MESSAGE_DATA = test_utils.load_template_test_data(TEST_MODULE_NAME,
                                                                      'test_generate_clock_message.json')

TEST_PROCESS_CLOCK_HISTORY_ACTION_DATA = test_utils.load_template_test_data(TEST_MODULE_NAME,
                                                                            'test_process_clock_history_action.json')

interactive_test_data = {'type': 'dialog_submission', 'token': 'test', 'action_ts': 'test', 'team': {'id': 'test',
                         'domain': 'test'}, 'user': {'id': 'test', 'name': 'test'}, 'channel': {'id': 'test',
                         'name': 'slack-bot-and-commands'}, 'submission': {'email': settings.INTRATIME_TEST_USER_EMAIL,
                         'password': settings.INTRATIME_TEST_USER_PASSWORD}, 'callback_id': 'test',
                         'response_url': 'test', 'state': ''}

# ----------------------------------------------------------------------------------------------------------------------


def test_validate_message():
    # BAD FORMATS
    assert not slack.validate_message(1234)
    assert not slack.validate_message({'BAD_FORMAT': 'BAD_FORMAT'})

    # VALID FORMATS
    assert slack.validate_message(TEXT)
    assert slack.validate_message(TEXT_ATTACHEMENT)

# ----------------------------------------------------------------------------------------------------------------------


def test_post_private_message(remove_test_file):
    # BAD CHANNEL
    assert slack.post_private_message(TEXT, 'BAD_CHANNEL', log_file=TEST_FILE) == codes.BAD_REQUEST_DATA
    assert check_if_log_exist(messages.make_message(3015, f"channel_not_found"), TEST_FILE, logger.ERROR)

    # BAD TOKEN
    assert slack.post_private_message(TEXT, SLACK_CHANNEL, log_file=TEST_FILE, token='BAD_TOKEN') == \
        codes.BAD_REQUEST_DATA
    assert check_if_log_exist(messages.make_message(3015, f"invalid_auth"), TEST_FILE, logger.ERROR)

    # BAD TEXT
    assert slack.post_private_message(1234, SLACK_CHANNEL, log_file=TEST_FILE) == codes.INVALID_VALUE
    assert check_if_log_exist(messages.make_message(3018, f"of message parameter"), TEST_FILE, logger.ERROR)

    # SUCCESS MESSAGES
    assert slack.post_private_message(TEXT, SLACK_CHANNEL) == codes.SUCCESS
    assert slack.post_private_message(TEXT_ATTACHEMENT, SLACK_CHANNEL, 'attachments') == codes.SUCCESS
    assert slack.post_private_message(TEXT_BLOCK, SLACK_CHANNEL, 'blocks') == codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def test_post_ephemeral_message(remove_test_file):
    # BAD CHANNEL
    assert slack.post_ephemeral_message(TEXT, 'BAD_CHANNEL', TEST_USER_ID, TEST_FILE) == codes.BAD_REQUEST_DATA
    assert check_if_log_exist(messages.make_message(3015, f"channel_not_found"), TEST_FILE, logger.ERROR)

    # BAD TOKEN
    assert slack.post_ephemeral_message(TEXT, SLACK_CHANNEL, TEST_USER_ID, TEST_FILE, 'BAD_TOKEN') \
        == codes.BAD_REQUEST_DATA
    assert check_if_log_exist(messages.make_message(3015, f"invalid_auth"), TEST_FILE, logger.ERROR)

    # BAD TEXT
    assert slack.post_ephemeral_message(1234, SLACK_CHANNEL, TEST_USER_ID, TEST_FILE) == codes.INVALID_VALUE
    assert check_if_log_exist(messages.make_message(3018, f"of message parameter"), TEST_FILE, logger.ERROR)

    # SUCCESS MESSAGES
    assert slack.post_ephemeral_message(TEXT, SLACK_CHANNEL, TEST_USER_ID) == codes.SUCCESS
    assert slack.post_ephemeral_message(TEXT_ATTACHEMENT, SLACK_CHANNEL, TEST_USER_ID) == codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('data, expected_decoded_data', TEST_DECODE_SLACK_ARGS_DATA)
def test_decode_slack_args(data, expected_decoded_data):
    assert slack.decode_slack_args(data) == expected_decoded_data

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('data, callback_id, expected_api_data', TEST_GET_API_DATA, ids=TEST_GET_API_NAMES)
def test_get_api_data(data, callback_id, expected_api_data):
    api_data = slack.get_api_data(data, callback_id)
    api_data['token'] = 'test'
    api_data['trigger_id'] = 'test'
    api_data['dialog'] = json.loads(api_data['dialog'])

    assert api_data == expected_api_data

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('data, expected_result', TEST_GENERATE_CLOCK_MESSAGE_DATA)
def test_generate_clock_message(data, expected_result):
    assert slack.generate_clock_message(data) == expected_result

# ----------------------------------------------------------------------------------------------------------------------


def test_process_clock_interactive_data(add_user, token, post_delete_user, post_clock_out):
    # Prepare data
    global interactive_test_data
    interactive_test_data['callback_id'] = 'clock'
    interactive_test_data['submission']['action'] = 'in'

    # Lauch clocking process
    try:
        slack.process_interactive_data(interactive_test_data)
    except requests.exceptions.MissingSchema:
        pass

    # Check if clocking has been registered
    clocking_check = intratime.get_user_clocks(token, time_utils.get_past_datetime_from_current_datetime(5),
                                               time_utils.get_current_date_time(),
                                               interactive_test_data['submission']['action'])

    assert len(clocking_check) > 0

# ----------------------------------------------------------------------------------------------------------------------


def test_process_sign_up_interactive_data(pre_delete_user, post_delete_user):
    # Prepare data
    global interactive_test_data
    interactive_test_data['callback_id'] = 'sign_up'

    # Lauch clocking process
    try:
        slack.process_interactive_data(interactive_test_data)
    except requests.exceptions.MissingSchema:
        pass

    assert user.user_exist(interactive_test_data['user']['id'])

# ----------------------------------------------------------------------------------------------------------------------


def test_process_update_user_interactive_data(add_user, post_delete_user):
    # Prepare data
    global interactive_test_data
    old_hash_password = user.get_user_data(interactive_test_data['user']['id'])['password']

    interactive_test_data['callback_id'] = 'update_user'

    # Lauch clocking process
    try:
        slack.process_interactive_data(interactive_test_data)
    except requests.exceptions.MissingSchema:
        pass

    assert user.get_user_data(interactive_test_data['user']['id'])['password'] != old_hash_password

# ----------------------------------------------------------------------------------------------------------------------


def test_process_delete_user_interactive_data(add_user, post_delete_user):
    # Prepare data
    global interactive_test_data
    interactive_test_data['callback_id'] = 'delete_user'

    # Lauch clocking process
    try:
        slack.process_interactive_data(interactive_test_data)
    except requests.exceptions.MissingSchema:
        pass

    assert not user.user_exist(interactive_test_data['user']['id'])

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('action, worked_hours, fake_datetime, data', TEST_PROCESS_CLOCK_HISTORY_ACTION_DATA)
def test_process_clock_history_action(action, worked_hours, fake_datetime, data, token):
    with freezegun.freeze_time(fake_datetime):
        assert slack.process_clock_history_action(token, action) == (worked_hours, data)
