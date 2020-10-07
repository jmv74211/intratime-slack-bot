from intratime_slack_bot.lib import logger
from intratime_slack_bot.config import settings

# ----------------------------------------------------------------------------------------------------------------------

ALIVE_MESSAGE = 'Alive'
BAD_DATA_MESSAGE = 'ERROR: Bad data request'
SUCCESS_MESSAGE = 'SUCCESS'
BAD_CREDENTIALS = 'Bad credentials'
BAD_INTRATIME_CONNECTION = 'Could not connect with intratime API'
BAD_INTRATIME_RESPONSE = 'Could not validate intratime API response'
BAD_TOKEN = 'Bad token'

# ----------------------------------------------------------------------------------------------------------------------


"""
Codes:
    DEBUG:    From 1000 to 1999
    INFO:     From 2000 to 2999
    ERROR:    From 3000 to 3999
    CRITICAL: From 4000 to 4999
"""

message = {
    "0": "Test message",
    "1000": "Got Intratime API token",
    "1001": "Bad intratime auth token when trying clocking",

    # ------------------------------------------------------------------------------------------------------------------

    "2000": "Registration done successfully",
    "2001": "User created successfully",
    "2002": "User deleted successfully",
    "2003": "User updated successfully",
    "2003": "User updated successfully",

    # ------------------------------------------------------------------------------------------------------------------

    "3000": "Could not get action from intratime module",
    "3001": "Could not get the message",
    "3002": "Request error. Could not connect with intratime service",
    "3003": "Could not get intratime auth token: Authentication failure",
    "3004": "Could not clock the action in intratime API. Check credentials and intratime API status service",
    "3005": "Bad user data",
    "3006": "Could not create the user",
    "3007": "User not found",
    "3008": "Could not delete the user",
    "3009": "Could not update the user",
    "3010": "Could not add the user, this user_id is already registered",
    "3011": "Could not update the user last registration date",
    "3012": "Could not find last_registration_date field",
    "3013": "Could not get the user_id",
    "3014": "Bad slack API credentials",
    "3015": "Bad request data",
    "3016": "Internal server error",
    "3017": "Undefined error",
    "3018": "Invalid value",

    # ------------------------------------------------------------------------------------------------------------------

    "4000": ''
}

# ----------------------------------------------------------------------------------------------------------------------


def get(code, log_file=settings.APP_LOG_FILE):
    """
    Function to get a custom message from message_id

    Parameters
    ----------
    code: int
        Message id
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
        (String): Message
    """
    try:
        return message[str(code)]
    except KeyError as exception:
        logger.log(file=log_file, level=logger.ERROR, message_id=3001)

# ----------------------------------------------------------------------------------------------------------------------


def make_message(code, custom_message):
    """
    Function to make a custom log message

    Parameters
    ----------
    code: int
        Message id
    custom_message: String
        Text to add to the message id content

    Returns
    -------
        (String): Combined message
    """

    try:
        new_custom_message = f"{message[str(code)]} {custom_message}"
    except KeyError:
        new_custom_message = f"Error, could not get message with ID = {code}"

    return new_custom_message

# ----------------------------------------------------------------------------------------------------------------------


def get_exception_message(exception):
    """
    Function get the exception message

    Parameters
    ----------
    exception: Exception
        Exception caught

    Returns
    -------
        (String): Exception message
    """

    if hasattr(exception, 'message'):
        return exception.message
    else:
        return str(exception)
