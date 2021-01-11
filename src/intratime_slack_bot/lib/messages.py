from intratime_slack_bot.lib import time_utils, intratime
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
NON_SLACK_REQUEST = 'Unauthorized. Only slack app can use this API.'
BAD_SLACK_HEADERS_REQUEST = f"{NON_SLACK_REQUEST} Missing 'X-Slack-Signature' and 'X-Slack-Request-Timestamp headers'"
BAD_SLACK_TIMESTAMP_REQUEST = f"{NON_SLACK_REQUEST} Bad timestamp"


# SLACK MESSAGES

ADD_USER_SUCCESS = ':heavy_check_mark: The user has been created successfully :heavy_check_mark:'
DELETE_USER_SUCCESS = ':heavy_check_mark: The user has been deleted successfully :heavy_check_mark:'
UPDATE_USER_SUCCESS = ':heavy_check_mark: The user info has been updated successfully :heavy_check_mark:'
CLOCKING_ACTION_SUCCESS = ':heavy_check_mark: Your clocking has been registered successfully :heavy_check_mark:'

IMAGE_BASE_URL = 'https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/ui/'

# ----------------------------------------------------------------------------------------------------------------------


"""
Codes:
    DEBUG:         From 1000 to 1999
    INFO/WARNING:  From 2000 to 2999
    ERROR:         From 3000 to 3999
"""

message = {
    "0": "Test message",
    "1000": "Got Intratime API token",

    # ------------------------------------------------------------------------------------------------------------------

    "2000": "Registration done successfully",
    "2001": "User created successfully",
    "2002": "User deleted successfully",
    "2003": "Slack message is too long to post it",
    "2004": "User updated successfully",

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
    "3019": "Could not get user clocks",
    "3020": "Bad intratime auth token when trying clocking",
    "3021": "Invalid history time range",
    "3022": "Could not validate the slack message",
    "3023": "Could not sent the private message",
    "3024": "Could not sent the ephemeral message",
    "3025": "Could not sent the ephemeral response message",
    "3026": "Could not find callback id",
    "3027": "Could not parse the request",
    "3028": "Could not validate user model",
    "3029": "Could not log user action",
    "3030": "Bad intratime credentials"
}

# ----------------------------------------------------------------------------------------------------------------------


def get(code, message_to_append=None):
    """
    Function to get a custom message from message_id

    Parameters
    ----------
    code: int
        Message id

    Returns
    -------
        (String): Message
    """

    try:
        if message_to_append is None:
            return message[str(code)]
        else:
            return f"{ message[str(code)]}: {message_to_append}"
    except KeyError as exception:
        return f"Error, could not get message with ID = {code}"

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
    def get_error_template(title, status_code, error_description):
        return [
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":x: {title} :x:\n *Status*: Failed {status_code}\n *Reason*: {error_description}\n"
                },
                "accessory": {
                    "type": "image",
                    "image_url": f"{IMAGE_BASE_URL}x.png",
                    "alt_text": "Error"
                }
            },
            {
                "type": "divider"
            }
        ]


    if key == 'ADD_USER_ERROR':
        return get_error_template('Could not add the user', parameters[0], 'Please contact with app administrator')
    elif key == 'DELETE_USER_ERROR':
        return get_error_template('Could not delete the user', parameters[0], 'Please contact with app administrator')
    elif key == 'UPDATE_USER_ERROR':
        return get_error_template('Could not update the user', parameters[0], 'Please contact with app administrator')
    elif key == 'CLOCKING_ERROR':
        return get_error_template('Could not clock your action', parameters[0], 'Please contact with app administrator')
    elif key == 'CLOCKING_CHECK_ERROR':
        return get_error_template('Could not verify this clocking request', parameters[0], 'Please, check manually ' \
                                  'that the clock has been done correctly')
    elif key == 'INVALID_CLOCKING_ACTION':
        return get_error_template('Could not clock your action', '', parameters[0])
    elif key == 'WORKED_TIME':
        return f":timer_clock: Your working time {parameters[0]} is *{parameters[1]}* :timer_clock:"
    else:
        return ''

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
            message += f"- *{command}*: {data['description']}\n {' ' * 10}_Accepted parameters_:" \
                       f" [`{', '.join(str(param) for param in data['allowed_parameters'])}`]\n"
        else:
            message += f"- *{command}*: {data['description']}\n"

    return write_slack_markdown(message)
