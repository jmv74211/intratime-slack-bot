# GLOBAL MESSAGES LIBRARY

## SLACK ERROR MESSAGES
INTRATIME_SERVICE_DOWN_MESSAGE = ':x: *Intratime service is down* :x: \n Please contact the administrator'
USER_SERVICE_DOWN_MESSAGE = ':x: *User service is down* :x: \n Please contact the administrator'
LOGGER_SERVICE_DOWN_MESSAGE = ':warning: *Logger service is down* :warning: \n Please contact the administrator'
FAIL_USER_CREATE_MESSAGE = ':x: *Sorry, the user could not be created* :x:'
FAIL_REGISTER_INTRATIME_MESSAGE = ':x: *Sorry, the request could not be registered* :x:'
FAIL_UPDATE_USER_MESSAGE = ':x: *Sorry, the user could not be updated* :x:'
FAIL_DELETE_USER_MESSAGE = ':x: *Sorry, the user could not be deleted* :x:'

## SLACK SUCCESS MESSAGES
USER_ADDED_SUCCESSFULLY_MESSAGE = ':heavy_check_mark: *User added successfully* :heavy_check_mark: \n \
  Now you can make registrations in intratime using `/register` command \n \
  You can also update your user data (`/update`) or delete it(`/delete`)'
SUCESSFULL_REGISTER_INTRATIME_MESSAGE = ':heavy_check_mark: *Successful registration* :heavy_check_mark:'
SUCCESSFULL_UPDATE_USER = ':heavy_check_mark: *User updated successfully* :heavy_check_mark:'
SUCCESSFULL_DELETE_USER = ':heavy_check_mark: *User deleted successfully* :heavy_check_mark:'

## API RESPONSES
SUCCESS_MESSAGE = 'SUCCESS'
USER_FOUND_MESSAGE = 'INFO: User found'
USERS_FOUND_MESSAGE = 'INFO: Users found'
BAD_DATA_MESSAGE = 'ERROR: Bad data request'
INTRATIME_CONNECT_ERROR_MESSAGE = 'Request error. Could not connect with intratime service'
USER_CONNECT_ERROR_MESSAGE = 'Request error. Could not connect with user service'
ALIVE_MESSAGE = 'Alive'
USER_NOT_FOUND_MESSAGE = 'ERROR: The user does not exist'
FAIL_ADD_USER_MESSAGE = 'ERROR: User could be not inserted'
FAIL_DELETE_USER_MESSAGE = 'ERROR: User could be not deleted'
FAIL_UPDATE_USER_MESSAGE = 'ERROR: User could be not updated. Maybe you wrote the same credentials'
FAIL_INTRATIME_REGISTER_MESSAGE = 'Registration failed'
WRONG_CREDENTIALS_MESSAGE = 'Wrong credentials'
TOKEN_INTRATIME_ERROR_MESSAGE = 'The request could not be sent to intratime API to get the token'

## DIALOGS VALIDATION MESSAGES
WRONG_CREDENTIALS_MESSAGE = 'Sorry, the username and/or password are not correct'
USER_NOT_REGISTERED_MESSAGE = 'Sorry, you are not registered'
WRONG_DATABASE_CREDENTIALS_MESSAGE = 'Sorry, the username and/or password from database data are not correct'
ALREADY_REGISTERED_MESSAGE = 'you are already registered'

## LOG ERROR MESSAGES
ADD_USER_ERROR = 'Could not add the user'
UPDATE_USER_ERROR = 'Could not update the user'
DELETE_USER_ERROR = 'Could not delete the user'
REGISTER_INTRATIME_ERROR = 'Could not register data in intratime'
PRIVATE_MESSAGE_ERROR = 'Could not send the private message'
EPHEMERAL_MESSAGE_ERROR = 'Could not send the ephemeral message'
WRONG_CALLBACK_ID = 'Wrong callback ID'

## BOT MESSAGES
IN_MESSAGE = 'iniciar la jornada laboral'
PAUSE_MESSAGE = 'realizar una pausa durante la jornada laboral'
RETURN_MESSAGE = 'volver a la jornada laboral tras una pausa'
LEAVE_MESSAGE = 'finalizar tu jornada laboral'