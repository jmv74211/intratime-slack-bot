import os
import json

from intratime_slack_bot.config import settings

TEST_DATA_PATH = os.path.join(settings.APP_PATH, 'test', 'data')

UNIT_TEST_DATA_PATH = os.path.join(TEST_DATA_PATH, 'unit')

# ----------------------------------------------------------------------------------------------------------------------


def read_file_data(input_file):
    with open(input_file, 'r') as file_data:
        json_data = json.loads(file_data.read())

    return json_data
