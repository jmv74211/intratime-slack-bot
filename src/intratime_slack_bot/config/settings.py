# APP SETTINGS file #
import os

MONGO_DB_USER = 'admin'  # os.environ['MONGO_DB_USER']
MONGO_DB_PASSWORD = 'admin'  # os.environ['MONGO_DB_PASSWORD']
MONGO_DB_PORT = '27017'
MONGO_DB_HOST = 'localhost'

APP_PATH = '/usr/local/app/development/intratime-slack-bot'
LOG_LEVEL = 'DEBUG'

APP_LOG_FILE = 'app.log'
INTRATIME_SERVICE_LOG_FILE = 'intratime.log'
USER_SERVICE_LOG_FILE = 'user.log'
SLACK_SERVICE_LOG_FILE = 'slack.log'

CIPHER_KEY = 'a1b2c3d4e5f6g7h8'  # os.environ['CIPHER_KEY']  # It must be 16 || 32 characters long

SLACK_API_USER_TOKEN = os.environ['SLACK_API_USER_TOKEN']
INTRATIME_TEST_USER_EMAIL = os.environ['INTRATIME_TEST_USER_EMAIL']
INTRATIME_TEST_USER_PASSWORD = os.environ['INTRATIME_TEST_USER_PASSWORD']

# SERVICE SETTINGS
PROTOCOL = 'http'
DEBUG_MODE = True

SLACK_SERVICE_HOST = '0.0.0.0'
SLACK_SERVICE_PORT = '10050'
