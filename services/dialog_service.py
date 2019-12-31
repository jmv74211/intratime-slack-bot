from flask import Flask, jsonify, request, make_response
import json
import os
import requests
import urllib.parse

app = Flask(__name__)
SLACK_DIALOG_API_URL = 'https://slack.com/api/dialog.open'
INTRATIME_SERVICE_URL = 'http://85.136.33.194:4000'

################################################################################################

def args_decode(data):

  data = data.split('&')
  output = {}
  for item in data:
    aux = item.split('=')
    output[aux[0]]=[aux[1]]

  output = json.loads(json.dumps(output).replace(']','').replace('[',''))

  return output

################################################################################################

def validate_credentials(user, password):

  check_credentials_user_url = INTRATIME_SERVICE_URL + '/check_user_credentials'
  payload = {'user': user, 'password': password }
  headers = {'content-type': 'application/json' }

  request = requests.get(check_credentials_user_url, json=payload, headers=headers)

  if request.status_code == 200:
    if request.json()['message'] == 'SUCCESS':
      return True
    else:
      return False
  else:
    # Log error
    print("REQUEST ERROR = {} - {}".format(request.text, request.status_code))
    return False

################################################################################################

@app.route("/interactive", methods=["POST"])
def get_interactive_data():
  try:
    data = urllib.parse.unquote(request.get_data().decode('utf-8'))
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  data = json.loads(data.replace('payload=','')) # Clean string to convert it to json format
  print("data = {}".format(data))

  print("Callback_id = {}".format(data['callback_id']))

  if data['callback_id'] == 'sign_up':
    # Validate credentials
    if not validate_credentials(data['submission']['email'], data['submission']['password']):
      return jsonify({'errors': [ {'name': 'email', 'error': 'Sorry, the username and/or password are not correct'},
        {'name': 'password', 'error': 'Sorry, the username and/or password are not correct'}]}), 200

    # Create new user in user service
  elif data['callback_id'] == 'register':
    print("Action = {}".format(data['submission']['action']))
    # Validate credentials
    # Get user data from user service
    # Register in intratime service
  elif data['callback_id'] == 'update_user':
    # Check if user already registered
    # Validate data
    # Update user in user service
    print("user_id = {}".format(data['user']['id']))
    print("email = {}".format(data['submission']['email']))
    print("password = {}".format(data['submission']['password']))
  elif data['callback_id'] == 'delete_user':
    # Check if user already registered
    # Delete user in user service
    print("Action = {}".format(data['submission']['delete']))

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
  elif callback_id == 'update_user':
    # Here I can query user data and set current value fields
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
              "value": "delete"
            }

          ]
        }
      ]
    }
  else:
    # Handle callback error
    pass

  api_data = {
    "token": os.environ['SLACK_API_TOKEN'],
    "trigger_id": data['trigger_id'],
    "dialog": json.dumps(dialog)
  }

  return api_data

################################################################################################

@app.route("/sign_up", methods=["POST"])
def sign_up():
  try:
    data = request.get_data().decode("utf-8")
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  api_data = get_api_data(data, 'sign_up')

  requests.post(SLACK_DIALOG_API_URL, data=api_data)

  return make_response("", 200)

################################################################################################

@app.route("/register", methods=["POST"])
def register():
  try:
    data = request.get_data().decode("utf-8")
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  api_data = get_api_data(data, 'register')
  requests.post(SLACK_DIALOG_API_URL, data=api_data)

  return make_response("", 200)

################################################################################################

@app.route("/update_user", methods=["POST"])
def update_user():
  try:
    data = request.get_data().decode("utf-8")
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  api_data = get_api_data(data, 'update_user')
  requests.post(SLACK_DIALOG_API_URL, data=api_data)

  return make_response("", 200)

################################################################################################

@app.route("/delete_user", methods=["POST"])
def delete_user():
  try:
    data = request.get_data().decode("utf-8")
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400
  print("antes")
  api_data = get_api_data(data, 'delete_user')
  print("despues = {}".format(api_data))
  req = requests.post(SLACK_DIALOG_API_URL, data=api_data)
  print("status code = {}".format(req.json()))
  return make_response("", 200)

#######################################  MAIN  ##################################################

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000, debug=True)