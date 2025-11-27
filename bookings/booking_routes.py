"""
Booking Routes
API endpoints for managing meeting room bookings.
"""
import sys
import os

# Add parent directory to path for shared_utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Blueprint, request, jsonify
from booking_model import (
    get_all_bookings,
    get_booking_by_id,
    get_user_bookings,
    get_room_bookings,
    check_room_availability,
    create_booking,
    update_booking,
    cancel_booking,
    get_conflicting_bookings,
    resolve_booking_conflict,
    get_stuck_bookings,
    unblock_stuck_booking
)

import jwt
from functools import wraps

SECRET_KEY = "4a0f2b0f392b236fe7ff4081c27260fc5520c88962bc45403ce18c179754ef5b"

# Try to import enhanced features
try:
    from shared_utils.audit_logger import log_request_response, log_admin_action
    FEATURES_ENABLED = True
except ImportError:
    # Fallback decorator that does nothing
    def log_request_response(func):
        return func
    def log_admin_action(*args, **kwargs):
        pass
    FEATURES_ENABLED = False

booking_bp = Blueprint('booking_bp', __name__)

# Initialize limiter (will be set by app)
limiter = None

def init_limiter(app_limiter):
    """
    Initialize rate limiter for this blueprint.
    
    Functionality:
        Sets the global rate limiter instance for the booking blueprint.
        This allows rate limiting to be applied to routes if configured.
    
    Parameters:
        app_limiter: The rate limiter instance from the Flask app.
    
    Returns:
        None
    """
    global limiter
    limiter = app_limiter


def apply_rate_limit_if_available(limit_str: str):
    """
    Helper to apply rate limit if limiter is available.
    
    Functionality:
        Returns a rate limit decorator if limiter is configured,
        otherwise returns a no-op decorator that does nothing.
    
    Parameters:
        limit_str (str): Rate limit string (e.g., "100/hour", "50/minute").
    
    Returns:
        function: Rate limit decorator if limiter exists, no-op decorator otherwise.
    """
    if limiter:
        return limiter.limit(limit_str)
    return lambda f: f  # No-op decorator if limiter not available


def token_required(f):
    """
    Decorator that validates JWT tokens from the Authorization header.
    
    Functionality:
        Validates JWT tokens from the Authorization header in the format
        "Bearer <token>". Extracts user information (username, role) from the
        token and stores it in request.user for use in route handlers.
        Returns 401 Unauthorized if token is missing, invalid, or expired.
    
    Parameters:
        f (function): The route handler function to be decorated.
    
    Returns:
        function: Decorated function that validates JWT tokens before execution.
        If validation fails, returns JSON response with error message and 401 status.
    
    Token Format:
        Authorization: Bearer <token>
    
    Raises:
        Returns 401 if:
            - Token is missing
            - Token format is invalid
            - Token is expired
            - Token is invalid
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
    
    Functionality:
        Checks if the authenticated user's role (from JWT token) matches
        one of the allowed roles. Must be used after @token_required decorator.
        Returns 403 Forbidden if user's role is not in the allowed roles list.
    
    Parameters:
        *roles (str): Variable number of allowed role names.
            Examples: "Admin", "Facility Manager", "Auditor", "regular user"
    
    Returns:
        function: Decorator function that checks user role before execution.
        If role check fails, returns JSON response with error message and 403 status.
    
    Raises:
        Returns 401 if user information is not found in token.
        Returns 403 if user's role is not in the allowed roles list.
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


def get_user_id_from_token():
    """
    Get user_id from JWT token by looking up username in database.
    
    Functionality:
        Extracts username from the JWT token stored in request.user and
        performs a database lookup to retrieve the corresponding user_id.
        This is necessary because JWT tokens contain username, not user_id.
    
    Parameters:
        None (uses request.user from token_required decorator)
    
    Returns:
        int or None: The user_id if found in database, None otherwise.
    
    Note:
        For better performance, consider including user_id directly in the
        JWT token payload to avoid database lookups.
    """
    if not hasattr(request, 'user') or 'username' not in request.user:
        return None
    
    try:
        # Try to get user_id from database using username
        conn = None
        try:
            from booking_model import connect_to_db
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM Users WHERE username = %s", (request.user["username"],))
            row = cur.fetchone()
            if row:
                return row[0]
        except Exception:
            pass
        finally:
            if conn:
                conn.close()
    except Exception:
        pass
    
    return None


def get_user_from_request():
    """
    Extract user information from JWT token.
    
    Functionality:
        Retrieves user_id (via database lookup) and role (from JWT token)
        for the authenticated user making the request.
    
    Parameters:
        None (uses request.user from token_required decorator)
    
    Returns:
        tuple: (user_id, user_role) where:
            - user_id (int or None): User ID from database lookup
            - user_role (str): User role from JWT token, defaults to "regular user"
        
        Returns (None, None) if request.user is not set.
    """
    if not hasattr(request, 'user'):
        return None, None
    
    user_id = get_user_id_from_token()
    user_role = request.user.get("role", "regular user")
    
    return user_id, user_role


@booking_bp.route('/api/bookings', methods=['GET'])
@token_required
@role_required("Admin", "Facility Manager", "Auditor")
@apply_rate_limit_if_available("100/hour")
@log_request_response
def api_get_all_bookings():
    """
    Get all bookings in the system.
    
    Functionality:
        Retrieves all bookings with user and room details.
        Only accessible to Admin, Facility Manager, and Auditor roles.
        Rate limited to 100 requests per hour.
    
    Parameters:
        None (uses JWT token from Authorization header)
    
    Returns:
        JSON response with status code 200 containing:
            {
                "bookings": [list of booking dictionaries],
                "count": number of bookings
            }
        
        Returns 401 if token is missing or invalid.
        Returns 403 if user role is not authorized.
    
    Authorization:
        Required roles: Admin, Facility Manager, Auditor
    """
    bookings = get_all_bookings()
    return jsonify({"bookings": bookings, "count": len(bookings)}), 200


@booking_bp.route('/api/bookings/<int:booking_id>', methods=['GET'])
@token_required
def api_get_booking(booking_id):
    """
    Get a specific booking by ID.
    
    Functionality:
        Retrieves a single booking by its ID. Regular users can only view
        their own bookings, while Admin, Facility Manager, and Auditor
        can view any booking.
    
    Parameters:
        booking_id (int): The ID of the booking to retrieve.
    
    Returns:
        JSON response with status code 200 containing booking details.
        
        Returns 401 if token is missing or invalid.
        Returns 403 if user tries to view another user's booking (regular users only).
        Returns 404 if booking is not found.
    
    Authorization:
        - Regular users: Can only view their own bookings
        - Admin, Facility Manager, Auditor: Can view any booking
    """
    user_id, user_role = get_user_from_request()
    
    booking = get_booking_by_id(booking_id)
    
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    if user_id and user_role not in ['Admin', 'Facility Manager', 'Auditor']:
        if booking.get('user_id') != user_id:
            return jsonify({"error": "Unauthorized: You can only view your own bookings"}), 403
    
    return jsonify(booking), 200


@booking_bp.route('/api/bookings/user/<int:user_id>', methods=['GET'])
@token_required
def api_get_user_bookings(user_id):
    """
    Get bookings for a specific user.
    
    Functionality:
        Retrieves all bookings for a given user. Regular users can only
        view their own booking history, while Admin, Facility Manager, and
        Auditor can view any user's booking history.
    
    Parameters:
        user_id (int): The ID of the user whose bookings to retrieve.
    
    Returns:
        JSON response with status code 200 containing:
            {
                "bookings": [list of booking dictionaries],
                "count": number of bookings,
                "user_id": user_id
            }
        
        Returns 401 if token is missing or invalid.
        Returns 403 if user tries to view another user's bookings (regular users only).
    
    Authorization:
        - Regular users: Can only view their own bookings
        - Admin, Facility Manager, Auditor: Can view any user's bookings
    """
    requesting_user_id, user_role = get_user_from_request()
    
    # Authorization check
    if requesting_user_id and user_role not in ['Admin', 'Facility Manager', 'Auditor']:
        if requesting_user_id != user_id:
            return jsonify({"error": "Unauthorized: You can only view your own booking history"}), 403
    
    bookings = get_user_bookings(user_id)
    return jsonify({"bookings": bookings, "count": len(bookings), "user_id": user_id}), 200


@booking_bp.route('/api/bookings/room/<int:room_id>', methods=['GET'])
def api_get_room_bookings(room_id):
    """
    Get bookings for a specific room.
    
    Functionality:
        Retrieves all bookings for a given room. Optionally filters by date
        if provided as a query parameter. This is a public endpoint (no authentication required).
    
    Parameters:
        room_id (int): The ID of the room whose bookings to retrieve.
        
        Query Parameters:
            date (str, optional): Filter bookings by date in YYYY-MM-DD format.
    
    Returns:
        JSON response with status code 200 containing:
            {
                "bookings": [list of booking dictionaries],
                "count": number of bookings,
                "room_id": room_id,
                "date": date filter (if provided)
            }
    
    Authorization:
        None (public endpoint)
    """
    booking_date = request.args.get('date')
    
    bookings = get_room_bookings(room_id, booking_date)
    return jsonify({"bookings": bookings, "count": len(bookings), "room_id": room_id, "date": booking_date}), 200


@booking_bp.route('/api/bookings/availability', methods=['GET'])
def api_check_availability():
    """
    Check room availability for a specific time slot.
    
    Functionality:
        Checks if a room is available for a given date and time range.
        This is a public endpoint (no authentication required).
    
    Parameters:
        Query Parameters (all required):
            room_id (int): The ID of the room to check.
            date (str): Date in YYYY-MM-DD format.
            start_time (str): Start time in HH:MM:SS format.
            end_time (str): End time in HH:MM:SS format.
    
    Returns:
        JSON response with status code 200 containing:
            {
                "room_id": room_id,
                "date": booking_date,
                "start_time": start_time,
                "end_time": end_time,
                "available": boolean indicating availability
            }
        
        Returns 400 if any required parameters are missing or invalid.
    
    Authorization:
        None (public endpoint)
    """
    room_id = request.args.get('room_id')
    booking_date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    if not all([room_id, booking_date, start_time, end_time]):
        return jsonify({"error": "Missing required parameters: room_id, date, start_time, end_time"}), 400
    
    try:
        room_id = int(room_id)
        is_available = check_room_availability(room_id, booking_date, start_time, end_time)
        return jsonify({
            "room_id": room_id,
            "date": booking_date,
            "start_time": start_time,
            "end_time": end_time,
            "available": is_available
        }), 200
    except ValueError:
        return jsonify({"error": "Invalid room_id"}), 400


@booking_bp.route('/api/bookings', methods=['POST'])
@token_required
@apply_rate_limit_if_available("50/hour")
@log_request_response
def api_create_booking():
    """
    Create a new booking.
    
    Functionality:
        Creates a new room booking. Regular users can only create bookings
        for themselves, while Admin and Facility Manager can create bookings
        for any user. Validates room availability before creating.
        Rate limited to 50 requests per hour.
    
    Parameters:
        Request Body (JSON, required):
            user_id (int): ID of the user making the booking.
            room_id (int): ID of the room to book.
            booking_date (str): Date in YYYY-MM-DD format.
            start_time (str): Start time in HH:MM:SS format.
            end_time (str): End time in HH:MM:SS format.
    
    Returns:
        JSON response with status code 201 containing created booking details.
        
        Returns 400 if:
            - No booking data provided
            - Room is not available
            - User or room does not exist
        Returns 401 if token is missing or invalid.
        Returns 403 if user tries to create booking for another user (regular users only).
        Returns 500 for other errors.
    
    Authorization:
        - Regular users: Can only create bookings for themselves
        - Admin, Facility Manager: Can create bookings for any user
    """
    user_id, user_role = get_user_from_request()
    booking_data = request.get_json()
    
    if not booking_data:
        return jsonify({"error": "No booking data provided"}), 400
    
    # Authorization: users can create bookings for themselves, admins can create for anyone
    requesting_user_id = booking_data.get('user_id')
    if user_id and user_role not in ['Admin', 'Facility Manager']:
        if requesting_user_id and int(requesting_user_id) != user_id:
            return jsonify({"error": "Unauthorized: You can only create bookings for yourself"}), 403
    
    result = create_booking(booking_data)
    
    if result.get('error'):
        status_code = 400 if 'not available' in result.get('error', '') or 'exist' in result.get('error', '') else 500
        return jsonify(result), status_code
    
    return jsonify(result), 201


@booking_bp.route('/api/bookings/<int:booking_id>', methods=['PUT'])
@token_required
def api_update_booking(booking_id):
    """
    Update an existing booking.
    
    Functionality:
        Updates an existing booking. Regular users can only update their own
        bookings, while Admin and Facility Manager can update any booking.
        Validates room availability if time/date/room is changed.
    
    Parameters:
        booking_id (int): The ID of the booking to update.
        
        Request Body (JSON, required):
            room_id (int, optional): New room ID.
            booking_date (str, optional): New date in YYYY-MM-DD format.
            start_time (str, optional): New start time in HH:MM:SS format.
            end_time (str, optional): New end time in HH:MM:SS format.
            status (str, optional): New booking status.
    
    Returns:
        JSON response with status code 200 containing updated booking details.
        
        Returns 400 if:
            - No booking data provided
            - Room is not available
            - Room does not exist
        Returns 401 if token is missing or invalid.
        Returns 403 if user tries to update another user's booking (regular users only).
    
    Authorization:
        - Regular users: Can only update their own bookings
        - Admin, Facility Manager: Can update any booking
    """
    user_id, user_role = get_user_from_request()
    booking_data = request.get_json()
    
    if not booking_data:
        return jsonify({"error": "No booking data provided"}), 400
    
    is_admin = user_role in ['Admin', 'Facility Manager']
    result = update_booking(booking_id, booking_data, user_id, is_admin)
    
    if result.get('error'):
        status_code = 403 if 'Unauthorized' in result.get('error', '') else 400
        return jsonify(result), status_code
    
    return jsonify(result), 200


@booking_bp.route('/api/bookings/<int:booking_id>/cancel', methods=['PUT'])
@token_required
def api_cancel_booking(booking_id):
    """
    Cancel a booking.
    
    Functionality:
        Cancels an existing booking by setting its status to 'Cancelled'.
        Regular users can only cancel their own bookings, while Admin and
        Facility Manager can cancel any booking.
    
    Parameters:
        booking_id (int): The ID of the booking to cancel.
    
    Returns:
        JSON response with status code 200 containing cancellation confirmation:
            {
                "message": "Booking cancelled successfully",
                "booking_id": booking_id,
                "status": "success"
            }
        
        Returns 400 if booking is already cancelled or other errors occur.
        Returns 401 if token is missing or invalid.
        Returns 403 if user tries to cancel another user's booking (regular users only).
    
    Authorization:
        - Regular users: Can only cancel their own bookings
        - Admin, Facility Manager: Can cancel any booking
    """
    user_id, user_role = get_user_from_request()
    
    is_admin = user_role in ['Admin', 'Facility Manager']
    result = cancel_booking(booking_id, user_id, is_admin)
    
    if result.get('error'):
        status_code = 403 if 'Unauthorized' in result.get('error', '') else 400
        return jsonify(result), status_code
    
    return jsonify(result), 200


@booking_bp.route('/api/admin/bookings/<int:booking_id>/force-cancel', methods=['PUT'])
@token_required
@role_required("Admin")
@log_request_response
def api_force_cancel_booking(booking_id):
    """
    Force cancel a booking (Admin only).
    
    Functionality:
        Allows admins to forcefully cancel any booking regardless of ownership.
        This action is logged for audit purposes.
    
    Parameters:
        booking_id (int): The ID of the booking to force cancel.
    
    Returns:
        JSON response with status code 200 containing cancellation confirmation.
        
        Returns 400 if booking cannot be cancelled or other errors occur.
        Returns 401 if token is missing or invalid.
        Returns 403 if user is not an Admin.
    
    Authorization:
        Required role: Admin
    """
    user_id, user_role = get_user_from_request()
    
    result = cancel_booking(booking_id, user_id, is_admin=True)
    
    if result.get('error'):
        return jsonify(result), 400
    
    # Log admin action
    if FEATURES_ENABLED:
        log_admin_action("Force cancelled booking", {"booking_id": booking_id})
    
    return jsonify(result), 200


@booking_bp.route('/api/admin/bookings/<int:booking_id>', methods=['PUT'])
@token_required
@role_required("Admin")
def api_admin_update_booking(booking_id):
    """
    Admin update booking endpoint.
    
    Functionality:
        Allows admins to override and update any booking, bypassing normal
        authorization checks. This is used for administrative corrections.
    
    Parameters:
        booking_id (int): The ID of the booking to update.
        
        Request Body (JSON, required):
            room_id (int, optional): New room ID.
            booking_date (str, optional): New date in YYYY-MM-DD format.
            start_time (str, optional): New start time in HH:MM:SS format.
            end_time (str, optional): New end time in HH:MM:SS format.
            status (str, optional): New booking status.
    
    Returns:
        JSON response with status code 200 containing updated booking details.
        
        Returns 400 if:
            - No booking data provided
            - Room is not available
            - Other validation errors
        Returns 401 if token is missing or invalid.
        Returns 403 if user is not an Admin.
    
    Authorization:
        Required role: Admin
    """
    user_id, user_role = get_user_from_request()
    
    booking_data = request.get_json()
    if not booking_data:
        return jsonify({"error": "No booking data provided"}), 400
    
    result = update_booking(booking_id, booking_data, user_id, is_admin=True)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@booking_bp.route('/api/admin/bookings/conflicts', methods=['GET'])
@token_required
@role_required("Admin")
def api_get_conflicts():
    """
    Get conflicting bookings for a time slot (Admin only).
    
    Functionality:
        Retrieves all bookings that conflict with a given time slot for a room.
        Used by admins to identify and resolve booking conflicts.
    
    Parameters:
        Query Parameters (all required):
            room_id (int): The ID of the room to check.
            date (str): Date in YYYY-MM-DD format.
            start_time (str): Start time in HH:MM:SS format.
            end_time (str): End time in HH:MM:SS format.
    
    Returns:
        JSON response with status code 200 containing:
            {
                "conflicts": [list of conflicting booking dictionaries],
                "count": number of conflicts,
                "room_id": room_id,
                "date": booking_date,
                "start_time": start_time,
                "end_time": end_time
            }
        
        Returns 400 if any required parameters are missing or invalid.
        Returns 401 if token is missing or invalid.
        Returns 403 if user is not an Admin.
    
    Authorization:
        Required role: Admin
    """
    room_id = request.args.get('room_id')
    booking_date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    if not all([room_id, booking_date, start_time, end_time]):
        return jsonify({"error": "Missing required parameters: room_id, date, start_time, end_time"}), 400
    
    try:
        room_id = int(room_id)
        conflicts = get_conflicting_bookings(room_id, booking_date, start_time, end_time)
        return jsonify({
            "conflicts": conflicts,
            "count": len(conflicts),
            "room_id": room_id,
            "date": booking_date,
            "start_time": start_time,
            "end_time": end_time
        }), 200
    except ValueError:
        return jsonify({"error": "Invalid room_id"}), 400


@booking_bp.route('/api/admin/bookings/<int:booking_id>/resolve', methods=['PUT'])
@token_required
@role_required("Admin")
def api_resolve_conflict(booking_id):
    """
    Resolve a booking conflict (Admin only).
    
    Functionality:
        Allows admins to resolve booking conflicts by taking actions such as
        cancelling, modifying, or overriding conflicting bookings.
    
    Parameters:
        booking_id (int): The ID of the booking to resolve.
        
        Request Body (JSON, required):
            action (str): Action to take. Options:
                - "cancel": Cancel the booking
                - "modify": Modify the booking (requires additional data)
                - "override": Override and keep the booking
    
    Returns:
        JSON response with status code 200 containing resolution confirmation.
        
        Returns 400 if:
            - No data provided
            - Invalid action specified
            - Booking not found
        Returns 401 if token is missing or invalid.
        Returns 403 if user is not an Admin.
    
    Authorization:
        Required role: Admin
    """
    user_id, user_role = get_user_from_request()
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    action = data.get('action', 'cancel')
    result = resolve_booking_conflict(booking_id, action, user_id)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@booking_bp.route('/api/admin/bookings/stuck', methods=['GET'])
@token_required
@role_required("Admin")
def api_get_stuck_bookings():
    """
    Get stuck bookings that need resolution (Admin only).
    
    Functionality:
        Retrieves bookings that are in stuck states (e.g., confirmed bookings
        with past dates that haven't been completed or cancelled).
        Used by admins to identify and fix booking inconsistencies.
    
    Parameters:
        None
    
    Returns:
        JSON response with status code 200 containing:
            {
                "stuck_bookings": [list of stuck booking dictionaries],
                "count": number of stuck bookings
            }
        
        Returns 401 if token is missing or invalid.
        Returns 403 if user is not an Admin.
    
    Authorization:
        Required role: Admin
    """
    stuck = get_stuck_bookings()
    return jsonify({"stuck_bookings": stuck, "count": len(stuck)}), 200


@booking_bp.route('/api/admin/bookings/<int:booking_id>/unblock', methods=['PUT'])
@token_required
@role_required("Admin")
def api_unblock_booking(booking_id):
    """
    Unblock a stuck booking (Admin only).
    
    Functionality:
        Allows admins to unblock stuck bookings by marking them as completed
        or cancelling them. This resolves booking state inconsistencies.
    
    Parameters:
        booking_id (int): The ID of the stuck booking to unblock.
        
        Request Body (JSON, optional):
            action (str): Action to take. Options:
                - "complete": Mark booking as completed (default)
                - "cancel": Cancel the booking
    
    Returns:
        JSON response with status code 200 containing unblock confirmation:
            {
                "message": "Booking marked as completed" or "Stuck booking cancelled",
                "booking_id": booking_id,
                "status": "success"
            }
        
        Returns 400 if:
            - Booking not found
            - Invalid action specified
        Returns 401 if token is missing or invalid.
        Returns 403 if user is not an Admin.
    
    Authorization:
        Required role: Admin
    """
    data = request.get_json() or {}
    action = data.get('action', 'complete')
    
    result = unblock_stuck_booking(booking_id, action)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@booking_bp.route('/api/circuit-breaker/status', methods=['GET'])
def api_get_circuit_breaker_status():
    """
    Get circuit breaker status for all services or a specific service.
    
    Functionality:
        Retrieves the current status of circuit breakers for microservices.
        Can return status for all services or filter by a specific service name.
        This is a public endpoint (no authentication required).
    
    Parameters:
        Query Parameters:
            service (str, optional): Service name to filter by.
                Options: 'users', 'rooms', 'bookings', 'reviews'
                If not provided, returns status for all services.
    
    Returns:
        JSON response with status code 200 containing circuit breaker status.
        
        Returns 503 if circuit breaker functionality is not available.
        Returns 500 for other errors.
    
    Authorization:
        None (public endpoint)
    """
    try:
        from shared_utils.circuit_breaker import get_circuit_breaker_status
        service_name = request.args.get('service')
        status = get_circuit_breaker_status(service_name)
        return jsonify(status), 200
    except ImportError:
        return jsonify({"error": "Circuit breaker not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@booking_bp.route('/api/circuit-breaker/reset/<service_name>', methods=['POST'])
@token_required
@role_required("Admin")
def api_reset_circuit_breaker(service_name):
    """
    Manually reset a circuit breaker (Admin only).
    
    Functionality:
        Allows admins to manually reset a circuit breaker for a specific service.
        This is useful when a service has recovered and the circuit breaker needs
        to be reset to allow requests through again.
    
    Parameters:
        service_name (str): Name of the service whose circuit breaker to reset.
            Options: 'users', 'rooms', 'bookings', 'reviews'
    
    Returns:
        JSON response with status code 200 containing reset confirmation.
        
        Returns 400 if reset fails or service name is invalid.
        Returns 401 if token is missing or invalid.
        Returns 403 if user is not an Admin.
        Returns 503 if circuit breaker functionality is not available.
        Returns 500 for other errors.
    
    Authorization:
        Required role: Admin
    """
    try:
        from shared_utils.circuit_breaker import reset_circuit_breaker
        result = reset_circuit_breaker(service_name)
        if result.get('error'):
            return jsonify(result), 400
        return jsonify(result), 200
    except ImportError:
        return jsonify({"error": "Circuit breaker not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

