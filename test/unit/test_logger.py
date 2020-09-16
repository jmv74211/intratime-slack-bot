import pytest
import json
import os
import re

from datetime import datetime
from intratime_slack_bot.lib import logger
from intratime_slack_bot.lib.test_utils import read_file_data, UNIT_TEST_DATA_PATH

# ----------------------------------------------------------------------------------------------------------------------


test_log_data = [item.values() for item in read_file_data(os.path.join(UNIT_TEST_DATA_PATH, 'logger', 'test_log.json'))]
test_file = 'test.log'

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def remove_file(request):
    yield
    os.remove(test_file)

# ----------------------------------------------------------------------------------------------------------------------


def test_get_current_date_time():
    now = datetime.now()
    date_time = f"{now.strftime('%Y-%m-%d')} {now.strftime('%H:%M:%S')}"

    assert date_time == logger.get_current_date_time()

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('level, message_id, custom_message, output', test_log_data)
def test_log(level, message_id, custom_message, output, remove_file):
    logger.log(test_file, level, message_id, custom_message)

    with open(test_file, 'r') as file:
        data = file.read()

    match_regex = rf'\[\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\] {output}'

    assert re.match(match_regex, data)
