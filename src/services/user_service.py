import pymongo
from flask import Flask, jsonify, request
from bson import json_util
import json
import sys
sys.path.insert(0, '../lib')
sys.path.insert(0, '../config')
import utils
import settings
import global_messages
import global_vars

myclient = pymongo.MongoClient(global_vars.MONGO_DB_SERVER)
intratime_db = myclient['intratime_db']
users_collection = intratime_db['users']

app = Flask(__name__)

#------------------------------------------------------------------------------#
#                             AUX FUNCTIONS                                    #
#------------------------------------------------------------------------------#

def check_user_exist(user_id):

  if users_collection.count_documents({ 'user_id': user_id}) <= 0 :
    return False

  return True

#-------------------------------------------------------------------------------

def validate_user_data(data):

  if data is None or 'user_id' not in data or 'username' not in data or 'password' not in data:
    return False

  return True

#-------------------------------------------------------------------------------

@app.route('/echo', methods=['GET'])
def echo_api():
  return jsonify({'message': global_messages.ALIVE_MESSAGE}), 200

#-------------------------------------------------------------------------------

@app.route('/user', methods=['GET'])
def list_users():

  user_list = []

  for user in users_collection.find():
    user_list.append(user)

  return jsonify({'message': global_messages.USERS_FOUND_MESSAGE,
    'data': json.loads(json_util.dumps(user_list))}), 200

#-------------------------------------------------------------------------------

@app.route('/user/<user_id>', methods=['GET'])
def get_user_info(user_id):

  if not check_user_exist(user_id):
    return jsonify({'message': global_messages.USER_NOT_FOUND_MESSAGE}), 200

  info_data = users_collection.find_one({'user_id': user_id})

  return jsonify({'message': global_messages.USER_FOUND_MESSAGE,
    'data': json.loads(json_util.dumps(info_data))}), 200

#-------------------------------------------------------------------------------

@app.route('/user', methods=['POST'])
def add_user():

  try:
    data = request.get_json()
  except:
    return jsonify({'message': global_messages.BAD_DATA_MESSAGE}), 400

  if not validate_user_data(data):
    return jsonify({'message': global_messages.BAD_DATA_MESSAGE}), 400

  if check_user_exist(data['user_id']):
    return jsonify({'message': global_messages.ALREADY_REGISTERED_MESSAGE}), 200

  ciphered_password = utils.encrypt(data['password']).decode(utils.ENCODING)

  insert_request = users_collection.insert_one({'user_id': data['user_id'], 'username': data['username'],
    'email': data['email'], 'password': ciphered_password})

  if insert_request.inserted_id is None:
    return jsonify({'message': global_messages.FAIL_ADD_USER_MESSAGE}), 400

  return jsonify({'message': global_messages.SUCCESS_MESSAGE}), 201

#-------------------------------------------------------------------------------

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):

  if not check_user_exist(user_id):
    return jsonify({'message': global_messages.USER_NOT_FOUND_MESSAGE}), 202

  delete_request = users_collection.delete_one({'user_id': user_id})

  if delete_request.deleted_count <= 0:
    return jsonify({'message': global_messages.FAIL_DELETE_USER_MESSAGE}), 400

  return jsonify({'message': global_messages.SUCCESS_MESSAGE}), 200

#-------------------------------------------------------------------------------

@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):

  try:
    data = request.get_json()
  except:
    return jsonify({'message': global_messages.BAD_DATA_MESSAGE}), 400

  if not validate_user_data(data):
    return jsonify({'message': global_messages.BAD_DATA_MESSAGE}), 400

  if not check_user_exist(user_id):
    return jsonify({'message': global_messages.USER_NOT_FOUND_MESSAGE}), 202

  data['password'] = utils.encrypt(data['password']).decode(utils.ENCODING)

  update_request = users_collection.update_one({'user_id': user_id}, {'$set': data})

  if update_request.modified_count <= 0:
    return jsonify({'message': global_messages.FAIL_UPDATE_USER_MESSAGE}), 400

  return jsonify({'message': global_messages.SUCCESS_MESSAGE}), 200

#------------------------------------------------------------------------------#
#                                  MAIN                                        #
#------------------------------------------------------------------------------#

if __name__ == '__main__':
  app.run(host=settings.USER_SERVICE_HOST, port=settings.USER_SERVICE_PORT, debug=settings.DEBUG_MODE)