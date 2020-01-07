from flask import Flask, jsonify, request, make_response
import json
import os
import requests
import urllib.parse
import sys
sys.path.insert(0, "../lib")
import utils
from functools import wraps

app = Flask(__name__)
SLACK_DIALOG_API_URL = 'https://slack.com/api/dialog.open'
INTRATIME_SERVICE_URL = 'http://127.0.0.1:4000'
USER_SERVICE_URL = 'http://127.0.0.1:5000'
LOGGER_SERVICE_URL = 'http://127.0.0.1:7000'
MODULE_NAME = 'Dialog-service'
ADMIN_USER = 'US6HV86ES'

################################################################################################

def args_decode(data):

  data = data.split('&')
  output = {}
  for item in data:
    aux = item.split('=')
    output[aux[0]] = [aux[1]]

  output = json.loads(json.dumps(output).replace(']','').replace('[',''))

  return output

################################################################################################

def services_are_running(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    data = args_decode(urllib.parse.unquote(request.get_data().decode('utf-8')))
    failed = False

    # Check intratime service
    try:
      requests.get('http://127.0.0.1:4000/echo')
    except:
      failed = True
      message = ':x: *Intratime service is down* :x: \n Please contact the administrator'
      post_ephemeral_message(message, data['response_url'])
      post_private_message(message, ADMIN_USER)

    # Check user service
    try:
      requests.get('http://127.0.0.1:5000/echo')
    except:
      failed = True
      message = ':x: *User service is down* :x: \n Please contact the administrator'
      post_ephemeral_message(message, data['response_url'])
      post_private_message(message, ADMIN_USER)

    # Log service
    try:
      requests.get('http://127.0.0.1:7000/echo')
    except:
      message = ':warning: *Logger service is down* :warning: \n Please notify the administrator'
      post_ephemeral_message(message, data['response_url'])
      post_private_message(message, ADMIN_USER)

    if failed:
      return make_response("", 200)

    return f(*args, **kwargs)

  return decorated

################################################################################################

def log(function, log_type, message):

  log_data_url = LOGGER_SERVICE_URL + '/log'
  payload = {'module': MODULE_NAME, 'function': function, 'type': log_type, 'message': message}
  headers = {'content-type': 'application/json'}

  request = requests.post(log_data_url, json=payload, headers=headers)

  if request.status_code != 200:
    return False

  return True

################################################################################################

def validate_credentials(email, password):

  check_credentials_user_url = INTRATIME_SERVICE_URL + '/check_user_credentials'
  payload = {'email': email, 'password': password}
  headers = {'content-type': 'application/json'}

  request = requests.get(check_credentials_user_url, json=payload, headers=headers)

  if request.status_code == 200:
    if request.json()['message'] == 'SUCCESS':
      return True
    else:
      return False
  else:
    log("validate_credentials", "ERROR", "Request error. Could not connect with intratime service. \
      Status code = {0}. Message = {}".format(request.status_code, request.text))
    return False

################################################################################################

def check_user_already_exists(user_id):

  check_user_already_exists_url = USER_SERVICE_URL + "/user/{}".format(user_id)
  request = requests.get(check_user_already_exists_url)

  if request.status_code == 200:
    if request.json()['message'] == 'INFO: User found':
      return True
    else:
      return False
  else:
    log("check_user_already_exists", "ERROR", "Request error. Could not connect with user service. \
      Status code = {0}. Message = {}".format(request.status_code, request.text))
    return False

################################################################################################

def get_user_credentials(user_id):

  get_user_credentials_url = USER_SERVICE_URL + "/user/{}".format(user_id)
  request = requests.get(get_user_credentials_url)

  if request.status_code == 200:
    if request.json()['message'] == 'INFO: User found':
      data = request.json()['data']
      # Decrypt the password
      data['password'] = utils.decrypt(data['password'].encode(utils.ENCODING)).decode('utf-8')
      return data
    else:
      return None
  else:
    log("get_user_credentials", "ERROR", "Request error. Could not connect with user service. \
      Status code = {0}. Message = {}".format(request.status_code, request.text))
    return None

################################################################################################

def validate_user_data(user_id):

  user_data = get_user_credentials(user_id)

  return validate_credentials(user_data['email'], user_data['password'])

################################################################################################

def add_user(user_id, username, email, password):

  add_user_url = USER_SERVICE_URL + '/user'
  payload = {'user_id': user_id, 'username': username, 'email': email, 'password': password}
  headers = {'content-type': 'application/json'}

  request = requests.post(add_user_url, json=payload, headers=headers)
  message = request.json()['message']

  if request.status_code == 201:
    return True, message
  else:
    return False, message

################################################################################################

def update_user(user_id, username, email, password):

  update_user_url = USER_SERVICE_URL + "/user/{}".format(user_id)
  payload = {'user_id': user_id, 'username': username, 'email': email, 'password': password}
  headers = {'content-type': 'application/json'}

  request = requests.put(update_user_url, json=payload, headers=headers)
  message = request.json()['message']

  if request.status_code == 200:
    return True, message
  else:
    return False, message

################################################################################################

def delete_user(user_id):

  delete_user_url = USER_SERVICE_URL + "/user/{}".format(user_id)
  payload = {'user_id': user_id}
  headers = {'content-type': 'application/json'}

  request = requests.delete(delete_user_url, json=payload, headers=headers)
  message = request.json()['message']

  if request.status_code == 200:
    return True, message
  else:
    return False, message

################################################################################################

def register_intratime_data(email, password, action):

  register_intratime_data_url = INTRATIME_SERVICE_URL + '/register'
  payload = {'email': email, 'password': password, 'action': action}
  headers = {'content-type': 'application/json'}

  request = requests.post(register_intratime_data_url, json=payload, headers=headers)
  message = request.json()['message']

  if request.status_code == 200:
    return True, ''
  else:
    return False, message

################################################################################################

def post_private_message(message, channel):

  payload = {'text': message, 'channel': channel, 'as_user': True}
  bot_token = "Bearer {}".format(os.environ['SLACK_API_TOKEN'])
  headers = {'content-type': 'application/json;charset=iso-8859-1', 'Authorization': bot_token}
  requests.post('https://slack.com/api/chat.postMessage', json=payload, headers=headers)

################################################################################################

def post_ephemeral_message(message, response_url):

  payload = {'text': message, 'response_type': 'ephemeral'}
  headers = {'content-type': 'application/json'}
  requests.post(response_url, json=payload, headers=headers)

################################################################################################

@app.route("/interactive", methods=["POST"])
def get_interactive_data():
  try:
    data = urllib.parse.unquote(request.get_data().decode('utf-8'))
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  data = json.loads(data.replace('payload=','')) # Clean string to convert it to json format

  if data['callback_id'] == 'sign_up':

    # Check if the user already exists
    if check_user_already_exists(data['user']['id']):
      return jsonify({'errors': [ {'name': 'email', 'error': 'Sorry, you are already registered'},]}), 200

    # Validate credentials
    if not validate_credentials(data['submission']['email'], data['submission']['password']):
      return jsonify({'errors': [ {'name': 'email', 'error': 'Sorry, the username and/or password are not correct'},
        {'name': 'password', 'error': 'Sorry, the username and/or password are not correct'}]}), 200

    # Create new user in user service
    add_user_data = add_user(data['user']['id'], data['user']['name'], data['submission']['email'],
      data['submission']['password'])

    if not add_user_data[0]: # If user is not added successfully
      post_ephemeral_message(":x: *Sorry, the user could not be created* :x: \n \
        {}".format(add_user_data[1]), data['response_url'])
      return make_response("", 200)

    post_ephemeral_message(":heavy_check_mark: *User added successfully* :heavy_check_mark: \n \
      Now you can make registrations in intratime using `/register` command \n \
      You can also update your user data (`/update`) or delete it(`/delete`)", data['response_url'])

  elif data['callback_id'] == 'register':

    # Validate credentials
    if not validate_user_data(data['user']['id']):
      return jsonify({'errors': [ {'name': 'email', 'error': 'Sorry, the username and/or password from database data are not correct'},
        {'name': 'password', 'error': 'Sorry, the username and/or password from database data are not correct'}]}), 200
    # Get user data from user service
    user_data = get_user_credentials(data['user']['id'])

     # Register in intratime service
    register_ok = register_intratime_data(user_data['email'], user_data['password'], data['submission']['action'])
    if not register_ok[0]:
      post_ephemeral_message(":x: *Sorry, the request could not be registered* :x: \n \
        {}".format(register_ok[1]), data['response_url'])
      return make_response("", 200)

    post_ephemeral_message(":heavy_check_mark: *Successful registration* :heavy_check_mark:", data['response_url'])

  elif data['callback_id'] == 'update_user':

    # Check if user already registered
    if not check_user_already_exists(data['user']['id']):
      return jsonify({'errors': [ {'name': 'email', 'error': 'Sorry, you are not registered'},]}), 200

    # Validate data
    if not validate_credentials(data['submission']['email'], data['submission']['password']):
      return jsonify({'errors': [ {'name': 'email', 'error': 'Sorry, the username and/or password are not correct'},
        {'name': 'password', 'error': 'Sorry, the username and/or password are not correct'}]}), 200

    # Update user in user service
    update_user_data = update_user(data['user']['id'], data['user']['name'], data['submission']['email'],
      data['submission']['password'])

    if not update_user_data[0]: # If user is not updated successfully
      post_ephemeral_message(":x: *Sorry, the user could not be updated* :x: \n \
        {}".format(update_user_data[1]), data['response_url'])
      return make_response("", 200)

    post_ephemeral_message(":heavy_check_mark: *User updated successfully* :heavy_check_mark:",
      data['response_url'])

  elif data['callback_id'] == 'delete_user':
    if not check_user_already_exists(data['user']['id']):
      return jsonify({'errors': [ {'name': 'delete', 'error': 'Sorry, you are not registered'},]}), 200

    # Delete user in user service
    if data['submission']['delete'] == 'confirm_delete':
      delete_user_data = delete_user(data['user']['id'])

      if not delete_user_data[0]: # If user is not deleted successfully
        post_ephemeral_message(":x: *Sorry, the user could not be deleted* :x: \n \
          {}".format(delete_user_data[1]), data['response_url'])
        return make_response("", 200)

    if data['submission']['delete'] == 'confirm_delete':
      post_ephemeral_message(":heavy_check_mark: *User deleted successfully* :heavy_check_mark:",
        data['response_url'])

  return make_response("", 200)

################################################################################################

def get_api_data(data, callback_id):

  data = args_decode(data) # x=1&y=2&z=3 to {x:1,y:2,z:3} format

  if callback_id == 'register':
    dialog = {
      "title": "Intratime: Register",
      "submit_label": "Submit",
      "callback_id": "register",
      "elements": [
        {
          "label": "Action",
          "type": "select",
          "name": "action",
          "options": [
            {
              "label": "Entry",
              "value": "in"
            },
            {
              "label": "Pause",
              "value": "pause"
            },
            {
              "label": "Return",
              "value": "return"
            },
            {
              "label": "Leave",
              "value": "out"
            }
          ]
        }
      ]
    }
  elif callback_id == 'sign_up':
    dialog = {
      "title": "Intratime: Sign up",
      "submit_label": "Submit",
      "callback_id": "sign_up",
      "elements": [
        {
          "label": "Intratime email",
          "name": "email",
          "type": "text",
          "subtype": "email",
          "placeholder": "you@example.com"
        },
        {
          "label": "Intratime password",
          "name": "password",
          "type": "text",
          "placeholder": "password"
        },
      ]
    }
  elif callback_id == 'update_user':
    dialog = {
      "title": "Intratime: Update user",
      "submit_label": "Submit",
      "callback_id": "update_user",
      "elements": [
        {
          "label": "Email Address",
          "name": "email",
          "type": "text",
          "subtype": "email",
          "placeholder": "you@example.com"
        },
        {
          "label": "Password",
          "name": "password",
          "type": "text",
          "placeholder": "password"
        },
      ]
    }
  elif callback_id == 'delete_user':
    dialog = {
      "title": "Intratime: Delete user",
      "submit_label": "Submit",
      "callback_id": "delete_user",
      "elements": [
        {
          "label": "Are you sure you want to delete the user?",
          "type": "select",
          "name": "delete",
          "options": [
            {
              "label": "No",
              "value": "cancel"
            },
            {
              "label": "Yes",
              "value": "confirm_delete"
            }

          ]
        }
      ]
    }
  else:
    log("get_api_data", "ERROR", "Callback id does not exist. Actual value = {}"
      .format(callback_id))
    return None

  api_data = {
    "token": os.environ['SLACK_API_TOKEN'],
    "trigger_id": data['trigger_id'],
    "dialog": json.dumps(dialog)
  }

  return api_data

################################################################################################

@app.route("/sign_up", methods=["POST"])
@services_are_running
def sign_up_api():
  try:
    data = request.get_data().decode("utf-8")
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  api_data = get_api_data(data, 'sign_up')
  requests.post(SLACK_DIALOG_API_URL, data=api_data)

  return make_response("", 200)

################################################################################################

@app.route("/register", methods=["POST"])
def register_api():
  try:
    data = request.get_data().decode("utf-8")
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  api_data = get_api_data(data, 'register')
  requests.post(SLACK_DIALOG_API_URL, data=api_data)

  return make_response("", 200)

################################################################################################

@app.route("/update_user", methods=["POST"])
def update_user_api():
  try:
    data = request.get_data().decode("utf-8")
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  api_data = get_api_data(data, 'update_user')
  requests.post(SLACK_DIALOG_API_URL, data=api_data)

  return make_response("", 200)

################################################################################################

@app.route("/delete_user", methods=["POST"])
def delete_user_api():
  try:
    data = request.get_data().decode("utf-8")
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  api_data = get_api_data(data, 'delete_user')
  requests.post(SLACK_DIALOG_API_URL, data=api_data)

  return make_response("", 200)

#######################################  MAIN  ##################################################

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000, debug=True)