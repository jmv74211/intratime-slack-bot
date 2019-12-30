import pymongo
from flask import Flask, jsonify, request

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

intratime_db = myclient["intratime_db"]

users_collection = intratime_db["users"]

app = Flask(__name__)

################################### AUX FUNCTIONS ##############################################

def check_user_exist(user_id):

  if users_collection.count_documents({ "user_id": user_id}) <= 0 :
    return False

  return True

################################################################################################

def validate_user_data(data):

  if data is None or 'user_id' not in data or 'username' not in data or 'password' not in data:
    return False

  return True

################################### API FUNCTIONS ##############################################

@app.route("/user", methods=["GET"])
def list_users():

  user_list = []

  for user in users_collection.find():
    user_list.append(user)

  return jsonify({'message': 'INFO: Users found', 'data': repr(user_list)}), 200

################################################################################################

@app.route("/user/<user_id>", methods=["GET"])
def get_user_info(user_id):

  if not check_user_exist(user_id):
    return jsonify({'message': 'ERROR: The user does not exist'}), 200

  info_data = users_collection.find({"user_id": user_id})

  return jsonify({'message': 'INFO: Users found', 'data': repr(info_data[0])}), 200

################################################################################################

@app.route("/user", methods=["POST"])
def add_user():

  try:
    data = request.get_json()
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  if not validate_user_data(data):
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  if check_user_exist(data['user_id']):
    return jsonify({'status': 'INFO: User already exists'}), 200

  insert_request = users_collection.insert_one({"user_id": data['user_id'], "username": data['username'],
    "password": data['password']})

  if insert_request.inserted_id is None:
    return jsonify({'message': 'ERROR: User could be not inserted'}), 400

  return jsonify({'message': 'INFO: Added'}), 201

################################################################################################

@app.route("/user/<user_id>", methods=["DELETE"])
def delete_user(user_id):

  if not check_user_exist(user_id):
    return jsonify({'message': 'WARNING: The user does not exist'}), 202

  delete_request = users_collection.delete_one({"user_id": user_id})

  if delete_request.deleted_count <= 0:
    return jsonify({'message': 'ERROR: User could be not deleted'}), 400

  return jsonify({'message': 'INFO: Deleted'}), 200

################################################################################################

@app.route("/user/<user_id>", methods=["PUT"])
def update_user(user_id):

  try:
    data = request.get_json()
  except:
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  if not validate_user_data(data):
    return jsonify({'status': 'ERROR: Bad data request'}), 400

  if not check_user_exist(user_id):
    return jsonify({'message': 'WARNING: The user does not exist'}), 202

  update_request = users_collection.update_one({"user_id": user_id}, {"$set": data})

  if update_request.modified_count <= 0:
    return jsonify({'message': 'ERROR: User could be not updated'}), 400

  return jsonify({'message': 'INFO: Updated'}), 200

#######################################  MAIN  ##################################################

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)







