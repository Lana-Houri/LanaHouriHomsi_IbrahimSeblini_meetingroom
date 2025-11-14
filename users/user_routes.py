from flask import Flask, request, jsonify
from flask_cors import CORS
from user_model import insert_user

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('api/users', methods = ['GET'])
def get_users():
    return jsonify(get_users())

@app.route('/api/users/<user_name>', methods=['GET'])
def get_user(user_name):
    return jsonify(get_user_by_name(user_name))

@app.route('/users/add', methods = ['POST'])
def add_user():
    user = request.get_json()
    return jsonify(insert_user(user))

