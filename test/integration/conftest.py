import pytest
import requests
import time
import os

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib import process, warehouse

BASE_URL = f"{settings.PROTOCOL}://{settings.INTRATIME_SERVICE_HOST}:{settings.INTRATIME_SERVICE_PORT}"
INTRATIME_SERVICE_PATH = os.path.join(settings.APP_PATH, 'src', 'intratime_slack_bot', 'services',
                                      'intratime_service.py')


# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope='module')
def launch_intratime_service(request):
    if not process.is_running(INTRATIME_SERVICE_PATH):
        pid = process.run(['python3', INTRATIME_SERVICE_PATH])
        time.sleep(3)
    yield
    if process.is_running(INTRATIME_SERVICE_PATH):
        process.stop(pid)

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope='module')
def token(request):
    TOKEN_DATA = {"email": settings.INTRATIME_TEST_USER_EMAIL, "password": settings.INTRATIME_TEST_USER_PASSWORD}
    request = requests.get(f"{BASE_URL}/{warehouse.GET_AUTH_TOKEN_REQUEST}", json=TOKEN_DATA)
    return request.json()['result']
