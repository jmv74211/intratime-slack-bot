from intratime_slack_bot.lib import logger, time_utils, intratime
from intratime_slack_bot.config import settings

# ----------------------------------------------------------------------------------------------------------------------

# API RESPONSE MESSAGES

ALIVE_MESSAGE = 'Alive'
BAD_DATA_MESSAGE = 'ERROR: Bad data request'
SUCCESS_MESSAGE = 'SUCCESS'
BAD_CREDENTIALS = 'Bad intratime credentials'
BAD_INTRATIME_CONNECTION = 'Could not connect with intratime API'
BAD_INTRATIME_RESPONSE = 'Could not validate intratime API response'
BAD_TOKEN = 'Bad token'
USER_ALREADY_REGISTERED = 'This user is already registered'
ADD_USER_ERROR = 'Could not add the user. Please contact with app administrator'
USER_NOT_FOUND = 'This user is not registered'
BAD_BD_CREDENTIALS = 'Bad intratime credentials. Please update the user (/update_user) with new credentials'

# SLACK MESSAGES

ADD_USER_SUCCESS = ':heavy_check_mark: The user has been created successfully :heavy_check_mark:'
DELETE_USER_SUCCESS = ':heavy_check_mark: The user has been deleted successfully :heavy_check_mark:'
UPDATE_USER_SUCCESS = ':heavy_check_mark: The user info has been updated successfully :heavy_check_mark:'
CLOCKING_ACTION_SUCCESS = ':heavy_check_mark: Your clocking has been registered successfully :heavy_check_mark:'

IMAGE_BASE_URL = 'https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/ui/'

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

# ----------------------------------------------------------------------------------------------------------------------


def set_custom_message(key, parameters):
    """
    Function to get a custom slack message

    Parameters
    ----------
    key: str
        Message key
    parameters: list
        List of parameters to add to the custom message

    Returns
    -------
    str:
        Custom slack message
    """

    if key == 'ADD_USER_ERROR':
        return f":x: Could not add the user. Status code = {parameters[0]}. Please contact with app administrator :x:"
    elif key == 'DELETE_USER_ERROR':
        return f":x: Could not delete the user. Status code = {parameters[0]}. Please contact with app administrator"\
                " :x:"
    elif key == 'UPDATE_USER_ERROR':
        return f":x: Could not update the user info. Status code = {parameters[0]}. Please contact with app " \
                "administrator :x:"
    elif key == 'CLOCKING_ERROR':
        return f":x: Could not clock your action. Status code = {parameters[0]}. Please contact with app " \
                "administrator :x:"
    elif key == 'CLOCKING_CHECK_ERROR':
        return f":x: Could not verify your last clocking. Status code = {parameters[0]}. Please, check manually or " \
                "by consulting your last clocks to verify this clocking action :x:"
    elif key == 'INVALID_CLOCKING_ACTION':
        return [
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":x: Could not clock your action :x:\n *Status*: Failed\n *Reason*: {parameters[0]}\n"
                },
                "accessory": {
                    "type": "image",
                    "image_url": f"{IMAGE_BASE_URL}x.png",
                    "alt_text": "Bad clocking action"
                }
            },
            {
                "type": "divider"
            }
        ]
    elif key == 'WORKED_TIME':
        return f":timer_clock: Your working time {parameters[0]} is *{parameters[1]}* :timer_clock:"
    else:
        return ""

# ----------------------------------------------------------------------------------------------------------------------


def write_slack_divider():
    """
    Function to write a slack divider

    Returns
    -------
    dict:
        Block message
    """

    return {
        "type": "divider"
    }

# ----------------------------------------------------------------------------------------------------------------------


def write_slack_markdown(message):
    """
    Function to write a slack markdown section

    Parameters
    ----------
    message: str
        Message

    Returns
    -------
    dict:
        Block message
    """

    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"{message}"
        }
    }

# ----------------------------------------------------------------------------------------------------------------------


def write_slack_header(message):
    """
    Function to write date message header

    Parameters
    ----------
    message: str
        Message to include in the header. In this case it cointains the clock register date

    Returns
    -------
    dict:
        Block message
    """

    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"{message}"
        }
    }

# ----------------------------------------------------------------------------------------------------------------------


def write_slack_message_too_long():
    """
    Function to write the warning message when the message size is too long.

    Returns
    -------
    List:
        Block message
    """

    return [
        write_slack_divider(),
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":warning: The message could not be displayed because it is too long :warning:"
            }
        },
        write_slack_divider()
    ]

# ----------------------------------------------------------------------------------------------------------------------


def write_slack_history_register(data):
    """
    Function to model the clock register content

    Parameters
    ----------
    data: dict
        Clock register data. It must contains action and datetime keys

    Returns
    -------
    dict:
        Block message
    """

    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Action*: {data['action'].upper()}\n *Datetime*: {data['datetime']}"
        },
        "accessory": {
            "type": "image",
            "image_url": f"{IMAGE_BASE_URL}{data['action']}_5.png",
            "alt_text": "Clocking action image"
        }
    }

# ----------------------------------------------------------------------------------------------------------------------


def generate_slack_history_report(token, action, data, worked_time, callback_id):
    """
    Function to build the slack history message

    Parameters
    ----------
    token: str
        Intratime authentication token
    action: str
       String enum: today_history, week_history or month_history
    data: list
       List with clock history data
    callback_id: str
       Callback id from history report

    Returns
    -------
    list:
        List with message blocks to send to slack
    """

    from intratime_slack_bot.lib import slack

    custom_message = {
        'today_history': {
            'title': 'TODAY',
            'from': f"{time_utils.get_current_date()} 00:00:00"
        },
        'week_history': {
            'title': 'WEEK',
            'from': f"{time_utils.get_first_week_day()}"
        },
        'month_history': {
            'title': 'MONTH',
            'from': f"{time_utils.get_first_month_day()}"
        }
    }

    header_text = f"{'-'*27} *{custom_message[action]['title']} HISTORY* {'-'*27}\n\n :calendar: From" \
                  f" _*{custom_message[action]['from']}*_ to _*{time_utils.get_current_date_time()}*_" \
                  f" :calendar:\n\n:timer_clock: Worked time: _*{worked_time}*_ :timer_clock:"

    blocks = [
        write_slack_divider(),
        write_slack_markdown(header_text),
        write_slack_divider()
    ]

    block_list = []

    if callback_id == slack.CLOCK_HISTORY_CALLBACK:
        data.reverse()

        if len(data) > 0:
            item_counter = 0
            day = ''

            while item_counter < len(data):
                if time_utils.get_day(data[item_counter]['datetime']) == day:
                    blocks.append(write_slack_history_register(data[item_counter]))
                    blocks.append(write_slack_divider())
                else:
                    block_list.append(blocks)
                    blocks = []
                    day = time_utils.get_day(data[item_counter]['datetime'])
                    date = time_utils.convert_datetime_string_to_date_string(data[item_counter]['datetime'])

                    blocks.append(write_slack_header(f"{date}"))
                    blocks.append(write_slack_divider())
                    blocks.append(write_slack_history_register(data[item_counter]))
                    blocks.append(write_slack_divider())

                item_counter += 1
        else:
            blocks.append(write_slack_markdown("No records available"))

        # Add last iteration block (while) or (else) blocks
        block_list.append(blocks)

    elif callback_id == slack.TIME_HISTORY_CALLBACK:
        datetime_to = f"{time_utils.get_current_date()} 23:59:59"
        block_list.append(blocks)

        if action == 'today_history':
            datetime_from = f"{time_utils.get_current_date()} 00:00:00"
        elif action == 'week_history':
            datetime_from = time_utils.get_first_week_day()
        elif action == 'month_history':
            datetime_from = time_utils.get_first_month_day()

        filtered_data = slack.filter_clock_history_data(data, datetime_from, datetime_to)
        worked_time_output = ''

        for worked_day, item_data in filtered_data.items():
            worked_time = intratime.get_worked_time(item_data)
            worked_time_output += f"*• {worked_day}*: {worked_time}\n"

        block_list.append([write_slack_markdown(worked_time_output)])

    return block_list

# ----------------------------------------------------------------------------------------------------------------------


def slack_warning_message(message):
    """
    Function to build a warning message

    Parameters
    ----------
    message: str
        Message

    Returns
    -------
    dict:
        Block message
    """

    return write_slack_markdown(f":warning: {message} :warning:")


# ----------------------------------------------------------------------------------------------------------------------

def slack_command_help():
    """
    Function to build the command help message

    Returns
    -------
    dict:
        Block message
    """

    from intratime_slack_bot.services.slack_service import ALLOWED_COMMANDS

    message = "Allowed commands and values:\n"

    for command, data in ALLOWED_COMMANDS.items():
        if len(data['allowed_parameters']) > 0:
            message += f"- *{command}*: {', '.join(str(param) for param in data['allowed_parameters'])}\n"
        else:
            message += f"- *{command}*\n"

    return write_slack_markdown(message)
