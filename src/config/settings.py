import os

##### APP SETTINGS #####

DEBUG_MODE = True

MONGO_DB_USER = os.environ['MONGO_DB_USER']
MONGO_DB_PASSWORD = os.environ['MONGO_DB_PASSWORD']
MONGO_DB_PORT = '27017'
MONGO_DB_HOST = 'mongo-service'

# MODULES_NAME
INTRATIME_SERVICE_NAME = 'intratime-service'
USER_SERVICE_NAME  = 'user-service'
LOGGER_SERVICE_NAME = 'logger-service'
DIALOG_SERVICE_NAME = 'dialog-service'

LOG_FILE = 'intratime_app.log' # Logs application errors

ADMIN_USER = 'US6HV86ES' # He will be alerted if any service is offline
SLACK_API_TOKEN = os.environ['SLACK_API_TOKEN']
CIPHER_KEY = os.environ['CIPHER_KEY']# It must be 16 || 32 characters long

# PORTS
DIALOG_SERVICE_PORT = '3000'
USER_SERVICE_PORT = '3001'
INTRATIME_SERVICE_PORT = '3002'
LOGGER_SERVICE_PORT = '3003'

# HOSTS
DIALOG_SERVICE_HOST = '0.0.0.0'
USER_SERVICE_HOST = '0.0.0.0'
INTRATIME_SERVICE_HOST = '0.0.0.0'
LOGGER_SERVICE_HOST = '0.0.0.0'
