import pytest
import os

from intratime_slack_bot.lib.test_utils import TEST_FILE

@pytest.fixture
def remove_test_file(request):
    yield
    os.remove(TEST_FILE)
