from flask import Flask, jsonify, request
import json
import random
import requests
from datetime import datetime

app = Flask(__name__)

INTRATIME_API_URL = "http://newapi.intratime.es"
INTRATIME_API_LOGIN_PATH =  "/api/user/login"
INTRATIME_API_CLOCKING_PATH = "/api/user/clocking"
INTRATIME_API_APPLICATION_HEADER = "Accept: application/vnd.apiintratime.v1+json"
INTRATIME_API_HEADER = {
                          "Accept": "application/vnd.apiintratime.v1+json",
                          "Content-Type": "application/x-www-form-urlencoded",
                          "charset":"utf8"
                        }

#------------------------------------------------------------------------------#
#                             AUX FUNCTIONS                                    #
#------------------------------------------------------------------------------#

def log_error(function, message):
  print("Function: {}\n Message: {}".format(function,message))
  # Here call logger service.

#-------------------------------------------------------------------------------

def get_current_date_time():

  now = datetime.now()
  date_time = "{0} {1}".format(now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))

  return date_time

#-------------------------------------------------------------------------------

def get_action(action):

  switcher = {
    "in": 0,
    "out": 1,
    "pause": 2,
    "return": 3,
  }

  try:
    return switcher[action]
  except:
    log_error("get_action", "Action error. Got {}".format(action))
    return -1

#-------------------------------------------------------------------------------

def get_random_coordinates():

  w = random.randint(1000,8324) # West of Greenwich meridian
  n = random.randint(5184,7163)  # North of Ecuador

  wazuh_location_w = float("37.147{0}".format(w))
  wazuh_location_n = float("-3.608{0}".format(n))

  return wazuh_location_w, wazuh_location_n

#-------------------------------------------------------------------------------
# Return codes: STRING_TOKEN: OK, -1: DATA_ERROR, -2: REQUEST_ERROR
def get_login_token(email, password):

  login_api_url = "{0}{1}".format(INTRATIME_API_URL, INTRATIME_API_LOGIN_PATH)
  payload="user={0}&pin={1}".format(email, password)

  try:
    request = requests.post(login_api_url, data=payload, headers=INTRATIME_API_HEADER)
  except:
    log_error("get_login_token", "Request error. Status code = {0}. Message = {}"
      .format(request.status_code, request.text))
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
  clocking_api_url = "{0}{1}".format(INTRATIME_API_URL, INTRATIME_API_CLOCKING_PATH)
  INTRATIME_API_HEADER.update({ "token": token })

  payload = "user_action={0}&user_use_server_time={1}&user_timestamp={2}&user_gps_coordinates={3},{4}" \
    .format(api_action, False, date_time, wazuh_location_w, wazuh_location_n)
  try:
    request = requests.post(clocking_api_url, data=payload, headers=INTRATIME_API_HEADER)
    if request.status_code == 201:
      return 0
    else:
      log_error("clocking", "Registration failed. Status code = {0}. Message = {}"
        .format(request.status_code, request.text))
      return -1
  except:
    log_error("clocking", "The request could not be sent to intratime API. Status code = {0}"
      .format(request.status_code))
    return -2

#------------------------------------------------------------------------------#
#                              API FUNCTIONS                                   #
#------------------------------------------------------------------------------#

@app.route("/check_user_credentials", methods=["GET"])
def check_credentials():

  try:
    data = request.get_json()
  except:
    data = None

  if data is None or not 'email' in data or not 'password' in data:
    return jsonify({'message': 'ERROR: Bad data'}), 400

  credentials_ok = check_user_credentials(data['email'], data['password'])

  if credentials_ok:
    return jsonify({'message': 'SUCCESS'}), 200
  else:
    return jsonify({'message': 'FAIL'}), 200

#-------------------------------------------------------------------------------

@app.route("/register", methods=["POST"])
def register():
  try:
    data = request.get_json()
  except:
    data = None

  if data is None or not 'email' in data or not 'password' in data or not 'action' in data:
    return jsonify({'message': 'ERROR: Bad data'}), 400

  token = get_login_token(data['email'], data['password'])

  if token == -1:
    return jsonify({'message': 'WARNING: Incorrect credentials'}), 202
  elif token == -2:
    return jsonify({'message': 'ERROR: Could not connect with intratime API'}), 500

  register_status = clocking(data['action'], token)

  if register_status == -1:
    return jsonify({'message': 'ERROR: Registration failed'}), 500
  elif register_status == -2:
    return jsonify({'message': 'ERROR: Could not connect with intratime AP'}), 500

  return jsonify({'message': 'SUCESS'}), 200

#------------------------------------------------------------------------------#
#                                  MAIN                                        #
#------------------------------------------------------------------------------#

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=4000, debug=True)