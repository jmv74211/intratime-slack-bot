from flask import Flask, jsonify, request, make_response
import json
import os
import requests

app = Flask(__name__)

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

@app.route("/register", methods=["POST"])
def test():
  try:
    data = request.get_data().decode("utf-8")
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  data = args_decode(data) # x=1&y=2&z=3 to {x:1,y:2,z:3} format

  api_url = 'https://slack.com/api/dialog.open'
  trigger_id = data['trigger_id']
  dialog={
    "title": "Intratime app sign up",
    "submit_label": "Submit",
    "callback_id": "add",
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

  api_data = {
    "token": os.environ['SLACK_API_TOKEN'],
    "trigger_id": trigger_id,
    "dialog": json.dumps(dialog)
  }
  res = requests.post(api_url, data=api_data)

  return make_response("", 200)

#######################################  MAIN  ##################################################

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000, debug=True)