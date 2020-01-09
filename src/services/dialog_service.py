from flask import Flask, jsonify, request, make_response
import json
import os
import requests
import urllib.parse
import sys
sys.path.insert(0, '../lib')
sys.path.insert(0, '../config')
import utils
import settings
import global_vars
import global_messages

from functools import wraps

app = Flask(__name__)

#------------------------------------------------------------------------------#
#                             AUX FUNCTIONS                                    #
#------------------------------------------------------------------------------#

def services_are_running(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    data = args_decode(urllib.parse.unquote(request.get_data().decode('utf-8')))
    failed = False

    # Check intratime service
    try:
      requests.get(global_vars.DIALOG_SERVICE_ECHO_REQUEST)
    except:
      failed = True
      post_ephemeral_message(global_messages.INTRATIME_SERVICE_DOWN_MESSAGE, data['response_url'])
      post_private_message(global_messages.INTRATIME_SERVICE_DOWN_MESSAGE, settings.ADMIN_USER)
      log('services_are_running', 'ERROR', global_messages.INTRATIME_SERVICE_DOWN_MESSAGE)

    # Check user service
    try:
      requests.get(global_vars.USER_SERVICE_ECHO_REQUEST)
    except:
      failed = True
      post_ephemeral_message(global_messages.USER_SERVICE_DOWN_MESSAGE, data['response_url'])
      post_private_message(global_messages.USER_SERVICE_DOWN_MESSAGE, settings.ADMIN_USER)
      log('services_are_running', 'ERROR', global_messages.USER_SERVICE_DOWN_MESSAGE)

    # Log service
    try:
      requests.get(global_vars.LOGGER_SERVICE_ECHO_REQUEST)
    except:
      post_private_message(global_messages.LOGGER_SERVICE_DOWN_MESSAGE, settings.ADMIN_USER)

    if failed:
      return make_response('', 200)

    return f(*args, **kwargs)

  return decorated

#-------------------------------------------------------------------------------

def args_decode(data):

  data = data.split('&')
  output = {}
  for item in data:
    aux = item.split('=')
    output[aux[0]] = [aux[1]]

  output = json.loads(json.dumps(output).replace(']','').replace('[',''))

  return output

#-------------------------------------------------------------------------------

def log(function, log_type, message):

  payload = {'module': global_vars.DIALOG_MODULE_NAME, 'function': function,
    'type': log_type, 'message': message}
  headers = {'content-type': 'application/json'}

  request = requests.post(global_vars.LOGGER_SERVICE_POST_LOG_REQUEST, json=payload, headers=headers)

  if request.status_code != 200:
    return False

  return True

#-------------------------------------------------------------------------------

def validate_credentials(email, password):

  payload = {'email': email, 'password': password}
  headers = {'content-type': 'application/json'}

  request = requests.get(global_vars.INTRATIME_SERVICE_CHECK_CREDENTIALS_REQUEST, json=payload,
    headers=headers)

  if request.status_code == 200:
    if request.json()['message'] == global_messages.SUCCESS_MESSAGE:
      return True
    else:
      return False
  else:
    log('validate_credentials', 'ERROR', "{} Status code = {}. Message = {}"
      .format(global_messages.INTRATIME_CONNECT_ERROR_MESSAGE,request.status_code, request.text))
    return False

#-------------------------------------------------------------------------------

def check_user_already_exists(user_id):

  request = requests.get("{}/{}".format(global_vars.USER_SERVICE_MANAGE_REQUEST, user_id))

  if request.status_code == 200:
    if request.json()['message'] == global_messages.USER_FOUND_MESSAGE:
      return True
    else:
      return False
  else:
    log('check_user_already_exists', 'ERROR', "{} Status code = {0}. Message = {}"
      .format(global_messages.USER_CONNECT_ERROR_MESSAGE, request.status_code, request.text))
    return False

#-------------------------------------------------------------------------------

def get_user_credentials(user_id):

  request = requests.get("{}/{}".format(global_vars.USER_SERVICE_MANAGE_REQUEST, user_id))

  if request.status_code == 200:
    if request.json()['message'] == global_messages.USER_FOUND_MESSAGE:
      data = request.json()['data']
      # Decrypt the password
      data['password'] = utils.decrypt(data['password'].encode(utils.ENCODING)).decode('utf-8')
      return data
    else:
      return None
  else:
    log('get_user_credentials', 'ERROR', "{} Status code = {0}. Message = {}"
      .format(global_messages.USER_CONNECT_ERROR_MESSAGE, request.status_code, request.text))
    return None

#-------------------------------------------------------------------------------

def validate_user_data(user_id):

  user_data = get_user_credentials(user_id)

  return validate_credentials(user_data['email'], user_data['password'])

#-------------------------------------------------------------------------------

def add_user(user_id, username, email, password):

  payload = {'user_id': user_id, 'username': username, 'email': email, 'password': password}
  headers = {'content-type': 'application/json'}

  request = requests.post(global_vars.USER_SERVICE_MANAGE_REQUEST, json=payload, headers=headers)
  message = request.json()['message']

  if request.status_code == 201:
    return True, message
  else:
    return False, message

#-------------------------------------------------------------------------------

def update_user(user_id, username, email, password):

  payload = {'user_id': user_id, 'username': username, 'email': email, 'password': password}
  headers = {'content-type': 'application/json'}

  request = requests.put("{}/{}".format(global_vars.USER_SERVICE_MANAGE_REQUEST, user_id),
    json=payload, headers=headers)

  message = request.json()['message']

  if request.status_code == 200:
    return True, message
  else:
    return False, message

#-------------------------------------------------------------------------------

def delete_user(user_id):

  payload = {'user_id': user_id}
  headers = {'content-type': 'application/json'}

  request = requests.delete("{}/{}".format(global_vars.USER_SERVICE_MANAGE_REQUEST, user_id),
    json=payload, headers=headers)

  message = request.json()['message']

  if request.status_code == 200:
    return True, message
  else:
    return False, message

#-------------------------------------------------------------------------------

def register_intratime_data(email, password, action):

  payload = {'email': email, 'password': password, 'action': action}
  headers = {'content-type': 'application/json'}

  request = requests.post(global_vars.INTRATIME_SERVICE_REGISTER_REQUEST,
    json=payload, headers=headers)
  message = request.json()['message']

  if request.status_code == 200:
    return True, ''
  else:
    return False, message

#-------------------------------------------------------------------------------

def post_private_message(message, channel):

  payload = {'text': message, 'channel': channel, 'as_user': True}
  bot_token = "Bearer {}".format(settings.SLACK_API_TOKEN)
  headers = {'content-type': 'application/json;charset=iso-8859-1', 'Authorization': bot_token}
  requests.post(global_vars.SLACK_POST_MESSAGE_URL, json=payload, headers=headers)

#-------------------------------------------------------------------------------

def post_ephemeral_message(message, response_url):

  payload = {'text': message, 'response_type': 'ephemeral'}
  headers = {'content-type': 'application/json'}
  requests.post(response_url, json=payload, headers=headers)

#-------------------------------------------------------------------------------

def get_api_data(data, callback_id):

  data = args_decode(data) # x=1&y=2&z=3 to {x:1,y:2,z:3} format

  if callback_id == 'register':
    dialog = {
      'title': 'Intratime: Register',
      'submit_label': 'Submit',
      'callback_id': 'register',
      'elements': [
        {
          'label': 'Action',
          'type': 'select',
          'name': 'action',
          'options': [
            {
              'label': 'Entry',
              'value': 'in'
            },
            {
              'label': 'Pause',
              'value': 'pause'
            },
            {
              'label': 'Return',
              'value': 'return'
            },
            {
              'label': 'Leave',
              'value': 'out'
            }
          ]
        }
      ]
    }
  elif callback_id == 'sign_up':
    dialog = {
      'title': 'Intratime: Sign up',
      'submit_label': 'Submit',
      'callback_id': 'sign_up',
      'elements': [
        {
          'label': 'Intratime email',
          'name': 'email',
          'type': 'text',
          'subtype': 'email',
          'placeholder': 'you@example.com'
        },
        {
          'label': 'Intratime password',
          'name': 'password',
          'type': 'text',
          'placeholder': 'password'
        },
      ]
    }
  elif callback_id == 'update_user':
    dialog = {
      'title': 'Intratime: Update user',
      'submit_label': 'Submit',
      'callback_id': 'update_user',
      'elements': [
        {
          'label': 'Email Address',
          'name': 'email',
          'type': 'text',
          'subtype': 'email',
          'placeholder': 'you@example.com'
        },
        {
          'label': 'Password',
          'name': 'password',
          'type': 'text',
          'placeholder': 'password'
        },
      ]
    }
  elif callback_id == 'delete_user':
    dialog = {
      'title': 'Intratime: Delete user',
      'submit_label': 'Submit',
      'callback_id': 'delete_user',
      'elements': [
        {
          'label': 'Are you sure you want to delete your user?',
          'type': 'select',
          'name': 'delete',
          'options': [
            {
              'label': 'No',
              'value': 'cancel'
            },
            {
              'label': 'Yes',
              'value': 'confirm_delete'
            }

          ]
        }
      ]
    }
  else:
    log('get_api_data', 'ERROR', "Callback id does not exist. Actual value = {}"
      .format(callback_id))
    return None

  api_data = {
    'token': settings.SLACK_API_TOKEN,
    'trigger_id': data['trigger_id'],
    'dialog': json.dumps(dialog)
  }

  return api_data

#------------------------------------------------------------------------------#
#                              API FUNCTIONS                                   #
#------------------------------------------------------------------------------#

@app.route('/interactive', methods=['POST'])
def get_interactive_data():
  try:
    data = urllib.parse.unquote(request.get_data().decode('utf-8'))
  except:
    return jsonify({'status': global_messages.BAD_DATA_MESSAGE}), 400

  data = json.loads(data.replace('payload=','')) # Clean string to convert it to json format

  if data['callback_id'] == 'sign_up':

    # Check if the user already exists
    if check_user_already_exists(data['user']['id']):
      return jsonify({'errors': [ {'name': 'email',
        'error': global_messages.ALREADY_REGISTERED_MESSAGE},]}), 200

    # Validate credentials
    if not validate_credentials(data['submission']['email'], data['submission']['password']):
      return jsonify({'errors': [ {'name': 'email', 'error': global_messages.WRONG_CREDENTIALS_MESSAGE},
        {'name': 'password', 'error': global_messages.WRONG_CREDENTIALS_MESSAGE}]}), 200

    # Create new user in user service
    add_user_data = add_user(data['user']['id'], data['user']['name'], data['submission']['email'],
      data['submission']['password'])

    if not add_user_data[0]: # If user is not added successfully
      post_ephemeral_message("{}\n{}".format(global_messages.FAIL_USER_CREATE_MESSAGE,
        add_user_data[1]), data['response_url'])
      return make_response('', 200)

    post_ephemeral_message(global_messages.USER_ADDED_SUCCESSFULLY_MESSAGE, data['response_url'])

  elif data['callback_id'] == 'register':

    # Check if user already registered
    if not check_user_already_exists(data['user']['id']):
      return jsonify({'errors': [ {'name': 'action', 'error': global_messages.USER_NOT_REGISTERED_MESSAGE},]}), 200

    # Validate credentials
    if not validate_user_data(data['user']['id']):
      return jsonify({'errors': [ {'name': 'email', 'error': global_messages.WRONG_DATABASE_CREDENTIALS_MESSAGE},
        {'name': 'password', 'error': global_messages.WRONG_DATABASE_CREDENTIALS_MESSAGE}]}), 200
    # Get user data from user service
    user_data = get_user_credentials(data['user']['id'])

     # Register in intratime service
    register_ok = register_intratime_data(user_data['email'], user_data['password'], data['submission']['action'])
    if not register_ok[0]:
      post_ephemeral_message("{}\n {}".format(global_messages.FAIL_REGISTER_INTRATIME_MESSAGE,
        register_ok[1]), data['response_url'])
      return make_response('', 200)

    post_ephemeral_message(global_messages.SUCESSFULL_REGISTER_INTRATIME_MESSAGE, data['response_url'])

  elif data['callback_id'] == 'update_user':

    # Check if user already registered
    if not check_user_already_exists(data['user']['id']):
      return jsonify({'errors': [ {'name': 'email', 'error': global_messages.USER_NOT_REGISTERED_MESSAGE},]}), 200

    # Validate data
    if not validate_credentials(data['submission']['email'], data['submission']['password']):
      return jsonify({'errors': [ {'name': 'email', 'error': global_messages.WRONG_CREDENTIALS_MESSAGE},
        {'name': 'password', 'error': global_messages.WRONG_CREDENTIALS_MESSAGE}]}), 200

    # Update user in user service
    update_user_data = update_user(data['user']['id'], data['user']['name'], data['submission']['email'],
      data['submission']['password'])

    if not update_user_data[0]: # If user is not updated successfully
      post_ephemeral_message("{}\n {}".format(global_messages.FAIL_UPDATE_USER_MESSAGE,
        update_user_data[1]), data['response_url'])
      return make_response('', 200)

    post_ephemeral_message(global_messages.SUCCESSFULL_UPDATE_USER, data['response_url'])

  elif data['callback_id'] == 'delete_user':
    if not check_user_already_exists(data['user']['id']):
      return jsonify({'errors': [ {'name': 'delete', 'error': global_messages.USER_NOT_REGISTERED_MESSAGE},]}), 200

    # Delete user in user service
    if data['submission']['delete'] == 'confirm_delete':
      delete_user_data = delete_user(data['user']['id'])

      if not delete_user_data[0]: # If user is not deleted successfully
        post_ephemeral_message("{}\n {}".format(global_messages.FAIL_DELETE_USER_MESSAGE,
          delete_user_data[1]), data['response_url'])
        return make_response('', 200)

    if data['submission']['delete'] == 'confirm_delete':
      post_ephemeral_message(global_messages.SUCCESSFULL_DELETE_USER, data['response_url'])

  return make_response('', 200)

#-------------------------------------------------------------------------------

@app.route('/sign_up', methods=['POST'])
@services_are_running
def sign_up_api():
  try:
    data = request.get_data().decode('utf-8')
  except:
    return jsonify({'status': global_messages.BAD_DATA_MESSAGE}), 400

  api_data = get_api_data(data, 'sign_up')
  requests.post(global_vars.SLACK_OPEN_DIALOG_URL, data=api_data)

  return make_response('', 200)

#-------------------------------------------------------------------------------

@app.route('/register', methods=['POST'])
@services_are_running
def register_api():
  try:
    data = request.get_data().decode('utf-8')
  except:
    return jsonify({'status': global_messages.BAD_DATA_MESSAGE}), 400

  api_data = get_api_data(data, 'register')
  requests.post(global_vars.SLACK_OPEN_DIALOG_URL, data=api_data)

  return make_response('', 200)

#-------------------------------------------------------------------------------

@app.route('/update_user', methods=['POST'])
@services_are_running
def update_user_api():
  try:
    data = request.get_data().decode('utf-8')
  except:
    return jsonify({'status': global_messages.BAD_DATA_MESSAGE}), 400

  api_data = get_api_data(data, 'update_user')
  requests.post(global_vars.SLACK_OPEN_DIALOG_URL, data=api_data)

  return make_response('', 200)

#-------------------------------------------------------------------------------

@app.route('/delete_user', methods=['POST'])
@services_are_running
def delete_user_api():
  try:
    data = request.get_data().decode('utf-8')
  except:
    return jsonify({'status': global_messages.BAD_DATA_MESSAGE}), 400

  api_data = get_api_data(data, 'delete_user')
  requests.post(global_vars.SLACK_OPEN_DIALOG_URL, data=api_data)

  return make_response('', 200)

#------------------------------------------------------------------------------#
#                                  MAIN                                        #
#------------------------------------------------------------------------------#

if __name__ == '__main__':
  app.run(host=settings.DIALOG_SERVICE_HOST, port=settings.DIALOG_SERVICE_PORT, debug=settings.DEBUG_MODE)