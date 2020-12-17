# APP SETTINGS file #
import os

MONGO_DB_USER = os.environ['MONGO_DB_USER']
MONGO_DB_PASSWORD = os.environ['MONGO_DB_PASSWORD']
MONGO_DB_PORT = '27017'
MONGO_DB_HOST = 'localhost'

APP_PATH = '/usr/local/app/development/intratime-slack-bot'
LOG_LEVEL = 'DEBUG'

APP_PATH = '/usr/local/app/development/intratime-slack-bot'
LOGS_PATH = os.path.join(APP_PATH, 'logs')
LOGS_LEVEL = logging.INFO

CIPHER_KEY = os.environ['CIPHER_KEY']  # It must be 16 || 32 characters long

SLACK_API_USER_TOKEN = os.environ['SLACK_API_USER_TOKEN']
SLACK_API_BOT_TOKEN = os.environ['SLACK_API_BOT_TOKEN']
INTRATIME_TEST_USER_EMAIL = os.environ['INTRATIME_TEST_USER_EMAIL']
INTRATIME_TEST_USER_PASSWORD = os.environ['INTRATIME_TEST_USER_PASSWORD']

# SERVICE SETTINGS
PROTOCOL = 'http'
DEBUG_MODE = True

SLACK_SERVICE_HOST = '0.0.0.0'
SLACK_SERVICE_PORT = '10050'

# TESTING CONFIG
SLACK_TEST_USER_ID = os.environ['SLACK_TEST_USER_ID']
SLACK_TEST_CHANNEL = os.environ['SLACK_TEST_CHANNEL']
