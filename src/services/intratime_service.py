from flask import Flask, jsonify, request
import json
import random
import requests
from datetime import datetime
import sys
sys.path.insert(0, '../config')
sys.path.insert(0, '../lib')
import settings
import global_messages
import global_vars

app = Flask(__name__)

INTRATIME_API_URL = 'http://newapi.intratime.es'
INTRATIME_API_LOGIN_PATH =  '/api/user/login'
INTRATIME_API_CLOCKING_PATH = '/api/user/clocking'
INTRATIME_API_APPLICATION_HEADER = 'Accept: application/vnd.apiintratime.v1+json'
INTRATIME_API_HEADER = {
                          'Accept': 'application/vnd.apiintratime.v1+json',
                          'Content-Type': 'application/x-www-form-urlencoded',
                          'charset':'utf8'
                        }

#------------------------------------------------------------------------------#
#                             AUX FUNCTIONS                                    #
#------------------------------------------------------------------------------#

def log(function, log_type, message):

  payload = {'module': global_vars.INTRATIME_MODULE_NAME, 'function': function,
    'type': log_type, 'message': message}
  headers = {'content-type': 'application/json'}

  request = requests.post("{}/{}".format(settings.LOGGER_SERVICE_UR, '/log'),
    json=payload, headers=headers)

  if request.status_code != 200:
    return False

  return True

#-------------------------------------------------------------------------------

def get_current_date_time():

  now = datetime.now()
  date_time = "{} {}".format(now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))

  return date_time

#-------------------------------------------------------------------------------

def get_action(action):

  switcher = {
    'in': 0,
    'out': 1,
    'pause': 2,
    'return': 3,
  }

  try:
    return switcher[action]
  except:
    log('get_action','ERROR' ,"Action error. Got {}".format(action))
    return -1

#-------------------------------------------------------------------------------

def get_random_coordinates():

  w = random.randint(1000,8324) # West of Greenwich meridian
  n = random.randint(5184,7163)  # North of Ecuador

  wazuh_location_w = float("37.147{}".format(w))
  wazuh_location_n = float("-3.608{}".format(n))

  return wazuh_location_w, wazuh_location_n

#-------------------------------------------------------------------------------
# Return codes: STRING_TOKEN: OK, -1: AUTHENTICATION_ERROR, -2: REQUEST_ERROR
def get_login_token(email, password):

  payload="user={}&pin={}".format(email, password)

  try:
    request = requests.post("{}{}".format(INTRATIME_API_URL, INTRATIME_API_LOGIN_PATH),
      data=payload, headers=INTRATIME_API_HEADER)
  except:
    log('get_login_token', 'ERROR', global_messages.INTRATIME_CONNECT_ERROR_MESSAGE)
    return -2

  try:
    token = json.loads(request.text)['USER_TOKEN']
  except:
    return -1

  return token

#-------------------------------------------------------------------------------

def check_user_credentials(email, password):
  token = get_login_token(email, password)
  return token != -1 and token != -2

#-------------------------------------------------------------------------------
# Return codes: 0: OK, -1: REGISTRATION_FAIL, 2: REQUEST_ERROR
def clocking(action, token):

  date_time = get_current_date_time()

  wazuh_location_w, wazuh_location_n = get_random_coordinates()

  api_action = get_action(action) # in --> 0, out --> 1, pause --> 3, return --> 4
  clocking_api_url = "{}{}".format(INTRATIME_API_URL, INTRATIME_API_CLOCKING_PATH)
  INTRATIME_API_HEADER.update({ 'token': token })

  payload = "user_action={}&user_use_server_time={}&user_timestamp={}&user_gps_coordinates={},{}" \
    .format(api_action, False, date_time, wazuh_location_w, wazuh_location_n)
  try:
    request = requests.post(clocking_api_url, data=payload, headers=INTRATIME_API_HEADER)
    if request.status_code == 201:
      return 0
    else:
      log('clocking', 'ERROR', "{} Status code = {}. Message = {}"
        .format(global_messages.FAIL_INTRATIME_REGISTER_MESSAGE,request.status_code, request.text))
      return -1
  except:
    log('clocking', 'ERROR', global_messages.INTRATIME_CONNECT_ERROR_MESSAGE)
    return -2

#------------------------------------------------------------------------------#
#                              API FUNCTIONS                                   #
#------------------------------------------------------------------------------#

@app.route('/echo', methods=['GET'])
def echo_api():
  return jsonify({'message': global_messages.ALIVE_MESSAGE})

#-------------------------------------------------------------------------------

@app.route('/check_user_credentials', methods=['GET'])
def check_credentials():

  try:
    data = request.get_json()
  except:
    data = None

  if data is None or not 'email' in data or not 'password' in data:
    return jsonify({'message': global_messages.BAD_DATA_MESSAGE}), 400

  credentials_ok = check_user_credentials(data['email'], data['password'])

  if credentials_ok:
    return jsonify({'message': global_messages.SUCCESS_MESSAGE}), 200
  else:
    return jsonify({'message': global_messages.WRONG_CREDENTIALS_MESSAGE}), 200

#-------------------------------------------------------------------------------

@app.route('/register', methods=['POST'])
def register():
  try:
    data = request.get_json()
  except:
    data = None

  if data is None or not 'email' in data or not 'password' in data or not 'action' in data:
    return jsonify({'message': global_messages.BAD_DATA_MESSAGE}), 400

  token = get_login_token(data['email'], data['password'])

  if token == -1:
    return jsonify({'message': global_messages.WRONG_CREDENTIALS_MESSAGE}), 202
  elif token == -2:
    log('register', 'ERROR', "{} Status code = {}"
      .format(global_messages.TOKEN_INTRATIME_ERROR_MESSAGE, request.status_code))
    return jsonify({'message': global_messages.INTRATIME_CONNECT_ERROR_MESSAGE}), 500

  register_status = clocking(data['action'], token)

  if register_status == -1:
    return jsonify({'message': global_messages.FAIL_INTRATIME_REGISTER_MESSAGE}), 500
  elif register_status == -2:
    log('register', 'ERROR', "{} Status code = {}"
      .format(global_messages.INTRATIME_CONNECT_ERROR_MESSAGE, request.status_code))
    return jsonify({'message': global_messages.INTRATIME_CONNECT_ERROR_MESSAGE}), 500

  return jsonify({'message': global_messages.SUCCESS_MESSAGE}), 200

#------------------------------------------------------------------------------#
#                                  MAIN                                        #
#------------------------------------------------------------------------------#

if __name__ == '__main__':
  app.run(host=settings.INTRATIME_SERVICE_HOST, port=settings.INTRATIME_SERVICE_PORT, debug=settings.DEBUG_MODE)