from flask import Flask, jsonify, request
import json
from datetime import datetime

app = Flask(__name__)

LOG_FILE = 'intratime_app.log'

################################################################################################

def get_current_date_time():

  now = datetime.now()
  date_time = "{0} {1}".format(now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))

  return date_time

################################################################################################

@app.route("/echo", methods=['GET'])
def echo_api():
  return jsonify({'message': 'Alive'})

################################################################################################

@app.route("/log", methods=["POST"])
def add_log():

  try:
    data = request.get_json()
  except:
    data = None

  if not 'module' in data or not 'function' in data or not 'message' in data or not 'type' in data:
    return jsonify({'message': 'ERROR: Bad data request'}), 400

  date_time = get_current_date_time()

  log = "{0} - {1} - {2} - {3} - {4}\n".format(date_time, data['module'], data['function'],
    data['type'], data['message'])

  with open(LOG_FILE, "a") as log_file:
    log_file.write(log)

  return jsonify({'message': 'Added successfully'}), 200

################################################################################################

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=7000, debug=True)