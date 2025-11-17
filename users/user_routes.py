from flask import Blueprint, request, jsonify
from user_model import insert_user

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/api/users', methods = ['GET'])
def get_users():
    return jsonify(get_users())

@user_bp.route('/api/users/<user_name>', methods=['GET'])
def get_user(user_name):
    return jsonify(get_user_by_name(user_name))

@user_bp.route('/users/add', methods = ['POST'])
def add_user():
    user = request.get_json()
    return jsonify(insert_user(user))

@user_bp.route('/api/user/update', methods=['PUT'])
def update_user():
    user=request.get_json()
    return jsonify(update_user(user))

@user_bp.route('/api/users/delete/<user_name>', methods=['DELETE'])
def delete_user(user_name):
    return jsonify(delete_user(user_name))