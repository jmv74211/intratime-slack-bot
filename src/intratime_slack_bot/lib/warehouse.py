# Global variables #

from intratime_slack_bot.config import settings


# URLS
PROTOCOL = 'http'
MONGO_DB_SERVER = f"mongodb://{settings.MONGO_DB_USER}:{settings.MONGO_DB_PASSWORD}@{settings.MONGO_DB_HOST}:"\
                  f"{settings.MONGO_DB_PORT}/"

SLACK_POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
SLACK_POST_EPHEMERAL_MESSAGE_URL = 'https://slack.com/api/chat.postEphemeral'

# PATHS
ECHO_REQUEST = '/echo'
CHECK_USER_CREDENTIALS_REQUEST = '/check_user_credentials'
GET_AUTH_TOKEN_REQUEST = '/get_auth_token'
GET_USER_CLOCKS_REQUEST = '/get_user_clocks'
CLOCK_REQUEST = '/clocking'
