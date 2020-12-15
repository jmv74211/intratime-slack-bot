# Global variables #

from intratime_slack_bot.config import settings


# URLS
SLACK_POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
SLACK_POST_EPHEMERAL_MESSAGE_URL = 'https://slack.com/api/chat.postEphemeral'
SLACK_OPEN_DIALOG_URL = 'https://slack.com/api/dialog.open'

PROTOCOL = 'http'
MONGO_DB_SERVER = f"mongodb://{settings.MONGO_DB_USER}:{settings.MONGO_DB_PASSWORD}@{settings.MONGO_DB_HOST}:"\
                  f"{settings.MONGO_DB_PORT}/"

SLACK_SERVICE_BASE_URL = f"{settings.PROTOCOL}://{settings.SLACK_SERVICE_HOST}:{settings.SLACK_SERVICE_PORT}"

# API PATHS
ECHO_REQUEST = '/echo'
CLOCK_REQUEST = '/clock'
ADD_USER_REQUEST = '/sign_up'
UPDATE_USER_REQUEST = '/update_user'
DELETE_USER_REQUEST = '/delete_user'
INTERACTIVE_REQUEST = '/interactive'
CLOCK_HISTORY_REQUEST = '/clock_history'
TIME_HISTORY_REQUEST = '/time_history'
WORKED_TIME_REQUEST = '/time'
