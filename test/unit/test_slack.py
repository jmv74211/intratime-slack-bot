import pytest

from intratime_slack_bot.lib import slack, codes, messages, logger
from intratime_slack_bot.lib.test_utils import check_if_log_exist, TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------


SLACK_CHANNEL = 'C019Y34PK55'
TEXT = 'Test message'
TEXT_ATTACHEMENT = [{"text": "Test message 2"}]
TEST_USER_ID = 'US6HV86ES'

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
    assert slack.post_private_message(TEXT, 'BAD_CHANNEL', TEST_FILE) == codes.BAD_REQUEST_DATA
    assert check_if_log_exist(messages.make_message(3015, f"channel_not_found"), TEST_FILE, logger.ERROR)

    # BAD TOKEN
    assert slack.post_private_message(TEXT, SLACK_CHANNEL, TEST_FILE, 'BAD_TOKEN') == codes.BAD_REQUEST_DATA
    assert check_if_log_exist(messages.make_message(3015, f"invalid_auth"), TEST_FILE, logger.ERROR)

    # BAD TEXT
    assert slack.post_private_message(1234, SLACK_CHANNEL, TEST_FILE) == codes.INVALID_VALUE
    assert check_if_log_exist(messages.make_message(3018, f"of message parameter"), TEST_FILE, logger.ERROR)

    # SUCCESS MESSAGES
    assert slack.post_private_message(TEXT, SLACK_CHANNEL) == codes.SUCCESS
    assert slack.post_private_message(TEXT_ATTACHEMENT, SLACK_CHANNEL) == codes.SUCCESS

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
