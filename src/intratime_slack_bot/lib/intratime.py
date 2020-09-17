import requests

from intratime_slack_bot.lib import logger
from intratime_slack_bot.config import settings


INTRATIME_API_URL = 'http://newapi.intratime.es'
INTRATIME_API_LOGIN_PATH = '/api/user/login'
INTRATIME_API_CLOCKING_PATH = f'{INTRATIME_API_URL}/api/user/clocking'
INTRATIME_API_APPLICATION_HEADER = 'Accept: application/vnd.apiintratime.v1+json'
INTRATIME_API_HEADER = {
                            'Accept': 'application/vnd.apiintratime.v1+json',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'charset': 'utf8'
                        }



# ----------------------------------------------------------------------------------------------------------------------


def get_action(action, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """ Function to get the intratime action ID

    Parameters
    ----------
    action: str
        Action enum: ['in', 'out', 'pause', 'return']
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    int:
        ID associated with the action
    """

    switcher = {
        'in': 0,
        'out': 1,
        'pause': 2,
        'return': 3,
    }

    try:
        return switcher[action]
    except KeyError as excetion:
        logger.log(file=log_file, level=logger.ERROR, message_id=3000)
