from flask import Blueprint, request, jsonify
from user_model import (
    get_users, insert_user, get_user_by_username, update_user,
    delete_user, update_role, reset_password, update_own_profile,
    login_user, get_booking_history
)

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/admin/users", methods=["GET"])
def api_get_users():
    return jsonify(get_users())

@user_bp.route("/admin/users/<username>", methods=["GET"])
def api_get_user(username):
    return jsonify(get_user_by_username(username))

@user_bp.route("/admin/users/add", methods=["POST"])
def api_add_user():
    user = request.get_json()
    return jsonify(insert_user(user))

@user_bp.route("/admin/user/update", methods=["PUT"])
def api_update_user():
    data = request.get_json()
    return jsonify(update_user(data))

@user_bp.route("/admin/users/delete/<username>", methods=["DELETE"])
def api_delete_user(username):
    return jsonify(delete_user(username))

@user_bp.route("/admin/update/user_role", methods=["PUT"])
def api_update_role():
    data = request.get_json()
    return jsonify(update_role(data['username'], data['user_role']))

@user_bp.route('/admin/users/<username>/booking_history', methods=['GET'])
def api_admin_booking_history(username):

    history = get_booking_history(username)

    if history is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": username,
        "count": len(history),
        "bookings": history
    })

@user_bp.route("/api/admin/reset_password", methods=["PUT"])
def api_reset_password():
    data = request.get_json()
    return jsonify(reset_password(data['username'], data['new_password']))

@user_bp.route("/regular_user/<username>", methods=["GET"])
def api_get_regular_user(username):
    return jsonify(get_user_by_username(username))

@user_bp.route("/regular_user/update", methods=["PUT"])
def api_update_regular_user():
    data = request.get_json()
    return jsonify(update_own_profile(data))

@user_bp.route('/regular_user/<username>/booking_history', methods=['GET'])
def api_regular_user_booking_history(username):
    history = get_booking_history(username)

    if history is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": username,
        "count": len(history),
        "bookings": history
    }), 200

@user_bp.route("/facility_manager/<username>", methods=["GET"])
def api_get_facility_manager(username):
    return jsonify(get_user_by_username(username))

@user_bp.route("/facility_manager/update", methods=["PUT"])
def api_update_facility_manager():
    data = request.get_json()
    return jsonify(update_own_profile(data))

@user_bp.route("/auditor/users", methods=["GET"])
def api_auditor_users():
    return jsonify(get_users())

@user_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    result = login_user(username, password)

    if result is None:
        return jsonify({"error": "User not found"}), 404
    if result is False:
        return jsonify({"error": "Incorrect password"}), 401

    return jsonify({"message": "Login successful", "user": result}), 200



