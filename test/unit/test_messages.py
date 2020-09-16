import pytest
import os

from intratime_slack_bot.lib import messages
from intratime_slack_bot.lib.test_utils import read_file_data, UNIT_TEST_DATA_PATH

test_make_message_data = [item.values() for item in read_file_data(os.path.join(UNIT_TEST_DATA_PATH, 'messages',
                          'test_make_message.json'))]

@pytest.mark.parametrize('code, custom_message, output', test_make_message_data)
def test_make_message(code, custom_message, output):
    assert messages.make_message(code, custom_message) == output


def get_exception_message()
    try:
        exception = 1/0
    except ZeroDivisionError as e:
        exception = e

    assert messages.get_exception_message() == "division by zero"
