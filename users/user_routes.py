from flask import Blueprint, request, jsonify
from user_model import get_users, insert_user, get_user_by_name, update_user, delete_user, update_role, reset_password, update_own_profile

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/admin/users', methods = ['GET'])
def api_get_users():
    return jsonify(get_users())

@user_bp.route('/admin/users/<username>', methods=['GET'])
def get_user(username):
    return jsonify(get_user_by_name(username))

@user_bp.route('/admin/users/add', methods = ['POST'])
def add_user():
    user = request.get_json()
    return jsonify(insert_user(user))

@user_bp.route('/admin/user/update', methods=['PUT'])
def api_update_user():
    user=request.get_json()
    return jsonify(update_user(user))

@user_bp.route('/admin/users/delete/<username>', methods=['DELETE'])
def api_delete_user(username):
    return jsonify(delete_user(username))

@user_bp.route('/admin/update/user_role', methods=['PUT'])
def api_update_user_role():
    data = request.get_json()
    username = data.get('username')
    new_role = data.get('user_role')
    return jsonify(update_role(username, new_role))


@user_bp.route('/api/admin/reset_password', methods=['PUT'])
def admin_reset_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('new_password')
    return jsonify(reset_password(username, new_password))

@user_bp.route('/regular_user/<user_name>', methods=['GET'])
def get_regular_user(username):
    return jsonify(get_user_by_name(username))

@user_bp.route('/regular_user/update', methods=['PUT'])
def update_own_profile_route():
    user = request.get_json()
    return jsonify(update_own_profile(user))

@user_bp.route('/facility_manager/<user_name>', methods=['GET'])
def get_facility_manager_user(username):
    return jsonify(get_user_by_name(username))

@user_bp.route('/facility_manager/update', methods=['PUT'])
def update_own_profile():
    user = request.get_json()
    return jsonify(update_own_profile(user))
    
@user_bp.route('/auditor/users', methods = ['GET'])
def get_all_users():
    return jsonify(get_users())