import pytest
import requests
import time
import os

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db import user
from intratime_slack_bot.lib import process, warehouse, intratime

SLACK_SERVICE_PATH = os.path.join(settings.APP_PATH, 'src', 'intratime_slack_bot', 'services', 'slack_service.py')

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope='module')
def launch_slack_service(request):
    if not process.is_running(SLACK_SERVICE_PATH):
        pid = process.run(['python3', SLACK_SERVICE_PATH])
        time.sleep(3)
    yield
    if process.is_running(SLACK_SERVICE_PATH):
        process.stop(pid)
