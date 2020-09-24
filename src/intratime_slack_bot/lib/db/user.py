import pymongo

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db.database import validate_data, USER_COLLECTION, USER_MODEL
from intratime_slack_bot.lib import warehouse, logger, codes, messages

# ----------------------------------------------------------------------------------------------------------------------


def user_exist(user_id):
    """
    Function to check if an user is already registered

    Parameters
    ----------
    user_id: str
        user identifier

    Returns
    -------
    boolean:
        True if the user exists, False otherwise
    """

    if USER_COLLECTION.count_documents({'user_id': user_id}) <= 0:
        return False

    return True

# ----------------------------------------------------------------------------------------------------------------------


def add_user(data, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to add a user in the database

    Parameters
    ----------
    data: dict
        User data
    log_file: str
        Log file when the action will be logged in case of failure or success

    Returns
    -------
    int:
        codes.BAD_USER_DATA if the data structure is no correct (Missing fields...)
        codes.USER_ALREADY_EXIST if the user is already registered in the database
        codes.USER_CREATION_ERROR if the user could not be inserted to the database due to db error
        codes.SUCCESS if the user has been inserted successfully
    """

    if not validate_data(data, USER_MODEL):
        logger.log(file=log_file, level=logger.ERROR,
                   custom_message=messages.make_message(3005, f"Expected model {USER_MODEL} and got this data: {data}"))
        return codes.BAD_USER_DATA

    if user_exist(data['user_id']):
        logger.log(file=log_file, level=logger.ERROR, message_id=3010)
        return codes.USER_ALREADY_EXIST

    insert_request = USER_COLLECTION.insert_one(data)

    if insert_request.inserted_id is None:
        logger.log(file=log_file, level=logger.ERROR, message_id=3006)
        return codes.USER_CREATION_ERROR

    logger.log(file=log_file, level=logger.INFO, custom_message=messages.make_message(2001, f"Data = {data}"))
    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def delete_user(user_id, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to delete a user from the database

    Parameters
    ----------
    user_id: str
        User identifier
    log_file: str
        Log file when the action will be logged in case of failure or success

    Returns
    -------
    int:
        codes.USER_NOT_FOUND if the user_id does not correspond with a registered user
        codes.USER_DELETE_ERROR if the user could not be deleted from the database due to db error
        codes.SUCCESS if the user has been deleted successfully
    """

    if not user_exist(user_id):
        logger.log(file=log_file, level=logger.ERROR, message_id=3007)
        return codes.USER_NOT_FOUND

    delete_request = USER_COLLECTION.delete_one({'user_id': user_id})

    if delete_request.deleted_count <= 0:
        logger.log(file=log_file, level=logger.ERROR, message_id=3008)
        return codes.USER_DELETE_ERROR

    logger.log(file=log_file, level=logger.INFO, message_id=2002)
    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def update_user(user_id, new_data, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to update the user information in the database

    Parameters
    ----------
    user_id: str
        User identifier
    new_data: dict
        New user data
    log_file: str
        Log file when the action will be logged in case of failure or success

    Returns
    -------
    int:
        codes.USER_NOT_FOUND if the user_id does not correspond with a registered user
        codes.BAD_USER_DATA if the data structure is no correct (Missing fields...)
        codes.USER_UPDATE_ERROR if the user could not be update in the database due to db error
        codes.SUCCESS if the user has been updated successfully
    """

    if not user_exist(user_id):
        logger.log(file=log_file, level=logger.ERROR, message_id=3007)
        return codes.USER_NOT_FOUND

    if not validate_data(new_data, USER_MODEL):
        logger.log(file=log_file, level=logger.ERROR,
                   custom_message=messages.make_message(3005,
                                                        f"Expected model {USER_MODEL} and got this data: {new_data}"))
        return codes.BAD_USER_DATA

    update_request = USER_COLLECTION.update_one({'user_id': user_id}, {'$set': new_data})

    if update_request.modified_count <= 0:
        logger.log(file=log_file, level=logger.ERROR, message_id=3009)
        return codes.USER_UPDATE_ERROR

    logger.log(file=log_file, level=logger.INFO, message_id=2003)
    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def get_user_data(user_id, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to get the user information from the database

    Parameters
    ----------
    user_id: str
        User identifier
    log_file: str
        Log file when the action will be logged in case of failure or success

    Returns
    -------
    dict:
        User information
    int:
        codes.USER_NOT_FOUND if the user_id does not correspond with a registered user
    """

    if not user_exist(user_id):
        logger.log(file=log_file, level=logger.ERROR, message_id=3007)
        return codes.USER_NOT_FOUND

    user_data = USER_COLLECTION.find_one({'user_id': user_id})

    return user_data

# ----------------------------------------------------------------------------------------------------------------------


def get_all_users_data():
    """
    Function to get all users information from the database

    Returns
    -------
    list:
        List with user information
    """

    return [user for user in USER_COLLECTION.find()]


# ----------------------------------------------------------------------------------------------------------------------

def update_last_registration_datetime(user_id, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to update the last registration user info

    Parameters
    ----------
    user_id: str
        User identifier
    log_file: str
        Log file when the action will be logged in case of failure or success

    Returns
    -------
    int:
        codes.USER_NOT_FOUND if the user_id does not correspond with a registered user
        codes.USER_UPDATE_ERROR if the info could not be update in the database due to db error
        codes.SUCCESS if the data has been updated successfully
    """

    if not user_exist(user_id):
        logger.log(file=log_file, level=logger.ERROR, message_id=3007)
        return codes.USER_NOT_FOUND

    user_data = get_user_data(user_id)

    try:
        user_data['last_registration_date'] = logger.get_current_date_time()
    except KeyError:
        logger.log(file=log_file, level=logger.ERROR, message_id=3012)

    update_request = USER_COLLECTION.update_one({'user_id': user_id}, {'$set': user_data})

    if update_request.modified_count <= 0:
        logger.log(file=log_file, level=logger.ERROR, message_id=3011)
        return codes.USER_UPDATE_ERROR

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def get_user_id(email, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to update the last registration user info

    Parameters
    ----------
    email: str
        User email
    log_file: str
        Log file when the action will be logged in case of failure or success

    Returns
    -------
    str:
        user_id if the email is correct
    int:
        codes.BAD_USER_EMAIL if the email does not correspond with a registered user
    """

    user_data = USER_COLLECTION.find_one({"intratime_mail": email})

    if user_data is None:
        logger.log(file=log_file, level=logger.ERROR, custom_message=messages.make_message(3011,
                                                                                           f"with mail = {email}"))
        return codes.BAD_USER_EMAIL

    return user_data['user_id']
