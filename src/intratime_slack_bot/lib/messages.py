"""
Codes:
    DEBUG:    From 1000 to 1999
    INFO:     From 2000 to 2999
    ERROR:    From 3000 to 3999
    CRITICAL: From 4000 to 4999
"""

message = {
    "0": "Test message",
    "1000": "",

    # ------------------------------------------------------------------------------------------------------------------

    "2000": "",

    # ------------------------------------------------------------------------------------------------------------------

    "3000": "Could not get action from intratime module",

    # ------------------------------------------------------------------------------------------------------------------

    "4000": ''
}

# ----------------------------------------------------------------------------------------------------------------------


def make_message(code, custom_message):
    """ Function to make a custom log message

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
    """ Function get the exception message

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
