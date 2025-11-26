from flask import Blueprint, request, jsonify
from user_model import (
    get_users, insert_user, get_user_by_username, update_user,
    delete_user, update_role, reset_password, update_own_profile,
    login_user, get_booking_history
)

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/admin/users", methods=["GET"])
def api_get_users():
    """
    Functionality: this function returns the full list of users for the admin.

    Parameters: None

    Value: it will return a JSON dictionary of all the users with there information with status 200.
    """
    return jsonify(get_users())

@user_bp.route("/admin/users/<username>", methods=["GET"])
def api_get_user(username):
    """
    Functionality: the function will get a single user profile using their username for the admin to view.

    Parameters:
        - username: this parameter is used to  identify the user to fetch.

    Value: it will return a JSON dictionary of all the information for the user selected.
    """
    return jsonify(get_user_by_username(username))

@user_bp.route("/admin/users/add", methods=["POST"])
def api_add_user():
    """
    Functionality: this function will create a new user record using the submitted information.

    Parameters:
        - request a JSON body containing user_name, username, email, password, user_role.

    Value: it will return a JSON of the inserted user information and if an error occur it will return a JSON error.
    """
    user = request.get_json()
    if not user:
        return jsonify({"error": "No data provided"}), 400
    
    result = insert_user(user)
    
    if result is None:
        return jsonify({"error": "Failed to insert user"}), 500
    
    if isinstance(result, dict) and "error" in result:
        status_code = 400 if "constraint" in result.get("error", "").lower() or "already exists" in result.get("error", "").lower() or "Missing required field" in result.get("error", "") else 500
        return jsonify(result), status_code
    
    return jsonify(result), 201

@user_bp.route("/admin/user/update", methods=["PUT"])
def api_update_user():
    """
    Functionality: this function updates an existing user’s profile as an admin.

    Parameters:
        - request JSON body with fields expected by update_user.

    Value: it returns a JSON dictionary returned by update_user.
    """
    data = request.get_json()
    return jsonify(update_user(data))

@user_bp.route("/admin/users/delete/<username>", methods=["DELETE"])
def api_delete_user(username):
    """
    Functionality: the function deletes the specified user by their username.

    Parameters:
        - username: path parameter identifying the user to remove.

    Value: this function returns a JSON confirmation dictionary that the user has been deleted.
    """
    return jsonify(delete_user(username))

@user_bp.route("/admin/update/user_role", methods=["PUT"])
def api_update_role():
    """
    Functionality: this function changes the role assigned to a user.

    Parameters:
        - request JSON body with username and user_role.

    Value: returns a JSON dictionary produced by update_role that return the user information with the updated role.
    """
    data = request.get_json()
    return jsonify(update_role(data['username'], data['user_role']))

@user_bp.route('/admin/users/<username>/booking_history', methods=['GET'])
def api_admin_booking_history(username):
    """
    Functionality: this function will provide the booking history of a certain user to the admin.

    Parameters:
        - username: path parameter for the user whose history is requested.

    Value: it will return a JSON with username, count, and bookings. And it it didn't work then it will return a JSON error.
    """
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
    """
    Functionality: this function resets a user’s password through the admin interface.

    Parameters:
        - request JSON body containing username and new_password.

    Value: it will return a JSON dictionary from reset_password.
    """
    data = request.get_json()
    return jsonify(reset_password(data['username'], data['new_password']))

@user_bp.route("/regular_user/<username>", methods=["GET"])
def api_get_regular_user(username):
    """
    Functionality: this function will return the profile details for a regular user.

    Parameters:
        - username: path parameter for the user requesting their data.

    Value: it will return a JSON dictionary for the user.
    """
    return jsonify(get_user_by_username(username))

@user_bp.route("/regular_user/update", methods=["PUT"])
def api_update_regular_user():
    """
    Functionality: this function will allow a regular user to update their own profile.

    Parameters:
        - request JSON body expected by update_own_profile.

    Value:it will return a JSON dictionary returned by update_own_profile.
    """
    data = request.get_json()
    return jsonify(update_own_profile(data))

@user_bp.route('/regular_user/<username>/booking_history', methods=['GET'])
def api_regular_user_booking_history(username):
    """
    Functionality: this function will return the booking history for a regular user.

    Parameters:
        - username: path parameter for the user requesting their bookings.

    Value: it will return a JSON with username, count, bookings. If there is an error it will return an error JSON.
    """
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
    """
    Functionality: this function fetches profile data for a facility manager.

    Parameters:
        - username: path parameter identifying the facility manager.

    Value: it will return a JSON dictionary with user details.
    """
    return jsonify(get_user_by_username(username))

@user_bp.route("/facility_manager/update", methods=["PUT"])
def api_update_facility_manager():
    """
    Functionality: this function allows facility managers to update their own profile.

    Parameters:
        - request JSON body consumed by update_own_profile.

    Value: it will return a JSON dictionary from update_own_profile.
    """
    data = request.get_json()
    return jsonify(update_own_profile(data))

@user_bp.route("/auditor/users", methods=["GET"])
def api_auditor_users():
    """
    Functionality: this function will returns the list of users for auditors.

    Parameters:
        - None

    Value: it will return a JSON list of users.
    """
    return jsonify(get_users())

@user_bp.route('/login', methods=['POST'])
def api_login():
    """
    Functionality: this function authenticates a user and returns their profile on success.

    Parameters:
        - request JSON body containing username and password.

    Value: it will return a JSON message with user data and if there is an error it will return a JSON error. 
    """
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



