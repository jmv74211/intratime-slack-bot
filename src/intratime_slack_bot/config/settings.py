# APP SETTINGS file #
import os
import logging

# SERVER CONFIGURATION
APP_DOMAIN = 'jmv74211.makefile.es'

# DATABASE CONFIGURATION
MONGO_DB_USER = "<YOUR_MONGO_DB_USER>"
MONGO_DB_PASSWORD = "<YOUR_MONGO_DB_PASSWORD>"
MONGO_DB_PORT = '27017'
MONGO_DB_HOST = 'mongo-service'

# SERVICE CONFIGURATION
APP_PATH = '/app'
PROTOCOL = 'http'
DEBUG_MODE = False
SLACK_SERVICE_HOST = '0.0.0.0'
SLACK_SERVICE_PORT = '10050'

# LOGS CONFIGURATION
LOG_LEVEL = 'DEBUG'
LOGS_PATH = os.path.join(APP_PATH, 'logs')
LOGS_LEVEL = logging.INFO

# SECURITY CONFIGURATION
CIPHER_KEY = "<YOUR_CIPHER_KEY>"  # It must be 16 || 32 characters long

# SLACK CONFIGURATION
SLACK_APP_SIGNATURE = "<YOUR_SLACK_APP_SIGNATURE>"
SLACK_API_USER_TOKEN = "<YOUR_SLACK_API_USER_TOKEN>"
SLACK_API_BOT_TOKEN = "<YOUR_SLACK_API_BOT_TOKEN>"

# INTRATIME CONFIGURATION
INTRATIME_TEST_USER_EMAIL = "<YOUR_INTRATIME_TEST_USER_EMAIL>"
INTRATIME_TEST_USER_PASSWORD = "<YOUR_INTRATIME_TEST_USER_PASSWORD>"

# TESTING CONFIGURATION
SLACK_TEST_USER_ID = "<YOUR_SLACK_TEST_USER_ID>"
SLACK_TEST_CHANNEL = "<YOUR_SLACK_TEST_CHANNEL>"
