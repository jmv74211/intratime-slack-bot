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

CIPHER_KEY = 'a1b2c3d4e5f6g7h8'  # os.environ['CIPHER_KEY']  # It must be 16 || 32 characters long
