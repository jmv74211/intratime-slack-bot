from flask import Flask, jsonify, request
import json
from datetime import datetime
import sys
sys.path.insert(0, '../config')
sys.path.insert(0, '../lib')
import settings
import global_messages

app = Flask(__name__)

#-------------------------------------------------------------------------------

def get_current_date_time():

  now = datetime.now()
  date_time = "{} {}".format(now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))

  return date_time

#-------------------------------------------------------------------------------

@app.route('/echo', methods=['GET'])
def echo_api():
  return jsonify({'message': 'Alive'})

#-------------------------------------------------------------------------------

@app.route('/log', methods=['POST'])
def add_log():

  try:
    data = request.get_json()
  except:
    data = None

  if not 'module' in data or not 'function' in data or not 'message' in data or not 'type' in data:
    return jsonify({'message': global_messages.BAD_DATA_MESSAGE}), 400

  date_time = get_current_date_time()

  log = "{} - {} - {} - {} - {}\n".format(date_time, data['module'], data['function'],
    data['type'], data['message'])

  with open(settings.LOG_FILE, 'a') as log_file:
    log_file.write(log)

  return jsonify({'message': global_messages.SUCCESS_MESSAGE}), 200

#------------------------------------------------------------------------------#
#                                  MAIN                                        #
#------------------------------------------------------------------------------#

if __name__ == '__main__':
  app.run(host=settings.LOGGER_SERVICE_HOST, port=settings.LOGGER_SERVICE_PORT, debug=settings.DEBUG_MODE)