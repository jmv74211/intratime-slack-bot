import pytest
import json
import os
import re

from intratime_slack_bot.lib import logger, test_utils
from intratime_slack_bot.lib.test_utils import check_if_log_exist, TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------
TEST_MODULE_NAME = 'logger'

TEST_LOG_DATA = test_utils.load_template_test_data(TEST_MODULE_NAME, 'test_log.json')

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def remove_file(request):
    yield
    os.remove(TEST_FILE)

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('level, message_id, custom_message, output', TEST_LOG_DATA)
def test_log(level, message_id, custom_message, output, remove_file):
    logger.log(TEST_FILE, level, message_id, custom_message)

    assert check_if_log_exist(output, TEST_FILE)
