from flask import Blueprint, request, jsonify
from user_model import (
    get_users, insert_user, get_user_by_username, update_user,
    delete_user, update_role, reset_password, update_own_profile,
    login_user, get_booking_history
)

import jwt
import datetime
from functools import wraps

SECRET_KEY = "4a0f2b0f392b236fe7ff4081c27260fc5520c88962bc45403ce18c179754ef5b"

def generate_token(user):
    payload = {
        "username": user["username"],
        "role": user["user_role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token


def token_required(f):
    """
    Decorator that validates JWT tokens from the Authorization header.
    Extracts user information from the token and stores it in request.user.
    
    Token format: Authorization: Bearer <token>
    
    Returns:
        401 Unauthorized if token is missing, invalid, or expired
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Extract token from Authorization header
        if "Authorization" in request.headers:
            try:
                auth_header = request.headers["Authorization"]
                # Expected format: "Bearer <token>"
                parts = auth_header.split(" ")
                if len(parts) == 2 and parts[0] == "Bearer":
                    token = parts[1]
                else:
                    return jsonify({"error": "Token format must be: Bearer <token>"}), 401
            except Exception as e:
                return jsonify({"error": "Token format must be: Bearer <token>"}), 401

        if not token:
            return jsonify({"error": "Token missing. Please provide a valid token in Authorization header"}), 401

        # Validate and decode the token
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # Store user information in request for use in route handlers
            request.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired. Please login again"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401
        except Exception as e:
            return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """
    Decorator that ensures the user has one of the required roles.
    Must be used after @token_required decorator.
    
    Args:
        *roles: Variable number of allowed role names (e.g., "Admin", "regular user")
    
    Returns:
        403 Forbidden if user's role is not in the allowed roles list
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Ensure request.user exists (should be set by token_required)
            if not hasattr(request, 'user') or 'role' not in request.user:
                return jsonify({"error": "User information not found in token"}), 401
            
            # Check if user's role is in the allowed roles
            if request.user["role"] not in roles:
                return jsonify({
                    "error": "Forbidden: Your role cannot access this resource",
                    "required_roles": list(roles),
                    "your_role": request.user["role"]
                }), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/register", methods=["POST"])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400

    result = insert_user(data)

    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 400

    return jsonify({
        "message": "User registered successfully",
        "user": result
    }), 201


@user_bp.route('/login', methods=['POST'])
def api_login():
    """
    Login endpoint that authenticates users and generates JWT tokens.
    
    Flow:
    1. Validates that username and password are provided
    2. Checks if user exists in database via login_user()
    3. Verifies password is correct
    4. Generates JWT token with user role information
    5. Returns token to user for subsequent authenticated requests
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Missing request data"}), 400
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Check if user exists in database and verify password
    result = login_user(username, password)

    # User does not exist in database
    if result is None:
        return jsonify({"error": "User not found"}), 404
    
    # User exists but password is incorrect
    if result is False:
        return jsonify({"error": "Incorrect password"}), 401

    # User exists and password is correct - generate token
    try:
        token = generate_token(result)
        if not token:
            return jsonify({"error": "Failed to generate token"}), 500
        
        return jsonify({
            "message": "Login successful",
            "token": str(token),
            "user": result
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to generate token", "details": str(e)}), 500

@user_bp.route("/admin/users", methods=["GET"])
@token_required
@role_required("Admin")
def api_get_users():
    return jsonify(get_users())


@user_bp.route("/admin/users/<username>", methods=["GET"])
@token_required
@role_required("Admin")
def api_get_user(username):
    return jsonify(get_user_by_username(username))


@user_bp.route("/admin/users/add", methods=["POST"])
@token_required
@role_required("Admin")
def api_add_user():
    user = request.get_json()
    if not user:
        return jsonify({"error": "No data provided"}), 400
    
    result = insert_user(user)
    
    if result is None:
        return jsonify({"error": "Failed to insert user"}), 500
    
    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 400
    
    return jsonify(result), 201


@user_bp.route("/admin/user/update", methods=["PUT"])
@token_required
@role_required("Admin")
def api_update_user():
    data = request.get_json()
    return jsonify(update_user(data))


@user_bp.route("/admin/users/delete/<username>", methods=["DELETE"])
@token_required
@role_required("Admin")
def api_delete_user(username):
    return jsonify(delete_user(username))


@user_bp.route("/admin/update/user_role", methods=["PUT"])
@token_required
@role_required("Admin")
def api_update_role():
    data = request.get_json()
    return jsonify(update_role(data['username'], data['user_role']))


@user_bp.route('/admin/users/<username>/booking_history', methods=['GET'])
@token_required
@role_required("Admin")
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
@token_required
@role_required("Admin")
def api_reset_password():
    data = request.get_json()
    return jsonify(reset_password(data['username'], data['new_password']))

@user_bp.route("/regular_user/<username>", methods=["GET"])
@token_required
@role_required("regular user")
def api_get_regular_user(username):
    if request.user["username"] != username:
        return jsonify({"error": "You cannot access another user's profile"}), 403
    return jsonify(get_user_by_username(username))


@user_bp.route("/regular_user/update", methods=["PUT"])
@token_required
@role_required("regular user")
def api_update_regular_user():
    data = request.get_json()

    if request.user["username"] != data["username"]:
        return jsonify({"error": "You cannot update another user's profile"}), 403

    return jsonify(update_own_profile(data))


@user_bp.route('/regular_user/<username>/booking_history', methods=['GET'])
@token_required
@role_required("regular user")
def api_regular_user_booking_history(username):

    if request.user["username"] != username:
        return jsonify({"error": "Unauthorized history access"}), 403

    history = get_booking_history(username)

    if history is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": username,
        "count": len(history),
        "bookings": history
    }), 200

@user_bp.route("/facility_manager/<username>", methods=["GET"])
@token_required
@role_required("Facility Manager")
def api_get_facility_manager(username):
    if request.user["username"] != username:
        return jsonify({"error": "You cannot access another user's profile"}), 403
    return jsonify(get_user_by_username(username))


@user_bp.route("/facility_manager/update", methods=["PUT"])
@token_required
@role_required("Facility Manager")
def api_update_facility_manager():
    data = request.get_json()

    if request.user["username"] != data["username"]:
        return jsonify({"error": "You cannot update another user's profile"}), 403

    return jsonify(update_own_profile(data))

@user_bp.route("/auditor/users", methods=["GET"])
@token_required
@role_required("Auditor")
def api_auditor_users():
    return jsonify(get_users())
