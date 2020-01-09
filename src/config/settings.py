import os

##### APP SETTINGS #####

DEBUG_MODE = True

MONGO_DB_SERVER = 'mongodb://172.16.1.31:27017/' # Mongo database server
LOG_FILE = 'intratime_app.log' # Logs application errors

ADMIN_USER = 'US6HV86ES' # He will be alerted if any service is offline
SLACK_API_TOKEN = os.environ['SLACK_API_TOKEN']
CIPHER_KEY = os.environ['cipher_key'] # It must be 16 || 32 characters long

# PORTS
DIALOG_SERVICE_PORT = '3000'
USER_SERVICE_PORT = '3001'
INTRATIME_SERVICE_PORT = '3002'
LOGGER_SERVICE_PORT = '3003'

# HOSTS
DIALOG_SERVICE_HOST = '0.0.0.0'
USER_SERVICE_HOST = '127.0.0.1'
INTRATIME_SERVICE_HOST = '127.0.0.1'
LOGGER_SERVICE_HOST = '127.0.0.1'
