# APP settings file

APP_PATH = '/usr/local/app/development/intratime-slack-bot'
LOG_LEVEL = 'DEBUG'

APP_LOG_FILE = 'app.log'
INTRATIME_SERVICE_LOG_FILE = 'intratime.log'

CIPHER_KEY = os.environ['CIPHER_KEY']  # It must be 16 || 32 characters long
