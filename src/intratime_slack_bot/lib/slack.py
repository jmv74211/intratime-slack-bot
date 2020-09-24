import requests
import time

from http import HTTPStatus

from intratime_slack_bot.lib import codes, warehouse, logger
from intratime_slack_bot.lib.messages import make_message
from intratime_slack_bot.config import settings

# ----------------------------------------------------------------------------------------------------------------------


def validate_message(message):
    """
    Function to validate a slack message to send

    Parameters
    ----------
    message: str
        Message to post

    Returns
    -------
    boolean:
        True if message format is valid, False otherwise
    """

    if isinstance(message, str):
        return True
    elif isinstance(message, list) and len(message) > 0 and isinstance(message[0], dict):
        return True

    return False

# ----------------------------------------------------------------------------------------------------------------------


def post_private_message(message, channel, log_file=settings.SLACK_SERVICE_LOG_FILE,
                         token=settings.SLACK_API_USER_TOKEN):
    """
    Function to post a private message in a slack channel

    Parameters
    ----------
    message: str
        Message to post
    channel: str
        Channel ID
    log_file: str
        Log file when the action will be logged in case of failure or success
    token: str
        Slack API user token

    Returns
    -------
    int:
        codes.INVALID_VALUE if the message_type parameter has invalid value
        codes.BAD_SLACK_API_AUTH_CREDENTIALS if the API request could not be resolved due to credentials issue
        codes.BAD_REQUEST_DATA if data sent is not correct
        codes.INTERNAL_SERVER_ERROR if there is some server error
        codes.UNDEFINED_ERROR if the error is unknown
        codes.SUCCESS if the message has ben posted successfully
    """

    if not validate_message(message):
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3018, f"of message parameter"))
        return codes.INVALID_VALUE

    time.sleep(1)  # Wait one second to send the API request due to rate limit (1/sec)

    headers = {'content-type': 'application/x-www-form-urlencoded', 'charset': 'utf8'}

    if isinstance(message, str):
        message_parameter = 'text'
    else:
        message_parameter = 'attachments'

    request = requests.post(f"{warehouse.SLACK_POST_MESSAGE_URL}?token={token}&channel={channel}&"
                            f"{message_parameter}={message}", headers=headers)

    if request.status_code != HTTPStatus.OK:
        if request.status_code != HTTPStatus.UNAUTHORIZED:
            logger.log(file=log_file, level=logger.ERROR, message_id=3014)
            return codes.BAD_SLACK_API_AUTH_CREDENTIALS
        elif request.status_code != HTTPStatus.BAD_REQUEST:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"Payload = {payload}"))
            return codes.BAD_REQUEST_DATA
        elif request.status_code != HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3016, f"when posting a message"))
            return codes.INTERNAL_SERVER_ERROR
        else:
            logger.log(file=log_file, level=logger.ERROR,
                       custom_message=make_message(3017, f"Status code = {request.status_code}"))
            return codes.UNDEFINED_ERROR

    if 'ok' in request.json() and request.json()['ok'] is False:
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"{request.json()['error']}"))
        return codes.BAD_REQUEST_DATA

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def post_ephemeral_message(message, channel, user_id, log_file=settings.SLACK_SERVICE_LOG_FILE,
                           token=settings.SLACK_API_USER_TOKEN):
    """
    Function to post a ephemeral message in a slack channel

    Parameters
    ----------
    message: str
        Message to post
    channel: str
        Channel ID
    user_id: str
        Destination user_id
    log_file: str
        Log file when the action will be logged in case of failure or success
    token: str
        Slack API user token

    Returns
    -------
    int:
        codes.INVALID_VALUE if the message_type parameter has invalid value
        codes.BAD_SLACK_API_AUTH_CREDENTIALS if the API request could not be resolved due to credentials issue
        codes.BAD_REQUEST_DATA if data sent is not correct
        codes.INTERNAL_SERVER_ERROR if there is some server error
        codes.UNDEFINED_ERROR if the error is unknown
        codes.SUCCESS if the message has ben posted successfully
    """

    if not validate_message(message):
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3018, f"of message parameter"))
        return codes.INVALID_VALUE

    time.sleep(1)  # Wait one second to send the API request due to rate limit (1/sec)

    headers = {'content-type': 'application/x-www-form-urlencoded', 'charset': 'utf8'}

    if isinstance(message, str):
        message_parameter = 'text'
    else:
        message_parameter = 'attachments'

    request = requests.post(f"{warehouse.SLACK_POST_EPHEMERAL_MESSAGE_URL}?token={token}&channel={channel}&"
                            f"{message_parameter}={message}&user={user_id}", headers=headers)

    if request.status_code != HTTPStatus.OK:
        if request.status_code != HTTPStatus.UNAUTHORIZED:
            logger.log(file=log_file, level=logger.ERROR, message_id=3014)
            return codes.BAD_SLACK_API_AUTH_CREDENTIALS
        elif request.status_code != HTTPStatus.BAD_REQUEST:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"Payload = {payload}"))
            return codes.BAD_REQUEST_DATA
        elif request.status_code != HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3016, f"when posting a message"))
            return codes.INTERNAL_SERVER_ERROR
        else:
            logger.log(file=log_file, level=logger.ERROR,
                       custom_message=make_message(3017, f"Status code = {request.status_code}"))
            return codes.UNDEFINED_ERROR

    if 'ok' in request.json() and request.json()['ok'] is False:
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"{request.json()['error']}"))
        return codes.BAD_REQUEST_DATA

    return codes.SUCCESS
