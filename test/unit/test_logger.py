import pytest
import json
import os
import re

from datetime import datetime
from intratime_slack_bot.lib import logger
from intratime_slack_bot.lib.test_utils import read_json_file_data, check_if_log_exist, UNIT_TEST_DATA_PATH, TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------


test_log_data = [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH, 'logger',
                                                               'test_log.json'))]

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def remove_file(request):
    yield
    os.remove(TEST_FILE)

# ----------------------------------------------------------------------------------------------------------------------


def test_get_current_date_time():
    now = datetime.now()
    date_time = f"{now.strftime('%Y-%m-%d')} {now.strftime('%H:%M:%S')}"

    assert date_time == logger.get_current_date_time()

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('level, message_id, custom_message, output', test_log_data)
def test_log(level, message_id, custom_message, output, remove_file):
    logger.log(TEST_FILE, level, message_id, custom_message)

    assert check_if_log_exist(output, TEST_FILE)
