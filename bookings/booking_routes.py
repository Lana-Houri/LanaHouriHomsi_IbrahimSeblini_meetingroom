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
    """Initialize rate limiter for this blueprint."""
    global limiter
    limiter = app_limiter


def apply_rate_limit_if_available(limit_str: str):
    """Helper to apply rate limit if limiter is available."""
    if limiter:
        return limiter.limit(limit_str)
    return lambda f: f  # No-op decorator if limiter not available


def get_user_from_request():
    """
    Extract user information from request headers.
    In a real implementation, this would verify JWT tokens or session.
    For now, we'll get user_id and role from headers.
    """
    user_id = request.headers.get('X-User-ID')
    user_role = request.headers.get('X-User-Role', 'regular user')
    
    if user_id:
        try:
            return int(user_id), user_role
        except ValueError:
            return None, None
    return None, None


@booking_bp.route('/api/bookings', methods=['GET'])
@apply_rate_limit_if_available("100/hour")
@log_request_response
def api_get_all_bookings():
    """
    Get all bookings.
    Admin, Facility Manager, and Auditor can view all bookings.
    Rate limited: 100 requests/hour
    """
    """
    Get all bookings.
    Admin, Facility Manager, and Auditor can view all bookings.
    """
    user_id, user_role = get_user_from_request()
    
    # Check authorization
    if user_role not in ['Admin', 'Facility Manager', 'Auditor']:
        return jsonify({"error": "Unauthorized: Only admins, facility managers, and auditors can view all bookings"}), 403
    
    bookings = get_all_bookings()
    return jsonify({"bookings": bookings, "count": len(bookings)}), 200


@booking_bp.route('/api/bookings/<int:booking_id>', methods=['GET'])
def api_get_booking(booking_id):
    """
    Get a specific booking by ID.
    Users can view their own bookings, admins/facility managers can view any.
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
def api_get_user_bookings(user_id):
    """
    Get bookings for a specific user.
    Users can view their own booking history, admins can view any user's history.
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
    Optional query parameter: date (YYYY-MM-DD) to filter by specific date.
    """
    booking_date = request.args.get('date')
    
    bookings = get_room_bookings(room_id, booking_date)
    return jsonify({"bookings": bookings, "count": len(bookings), "room_id": room_id, "date": booking_date}), 200


@booking_bp.route('/api/bookings/availability', methods=['GET'])
def api_check_availability():
    """
    Check room availability for a specific time slot.
    Query parameters: room_id, date, start_time, end_time
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
@apply_rate_limit_if_available("50/hour")
@log_request_response
def api_create_booking():
    """
    Create a new booking.
    Regular users, Facility Managers can create bookings.
    Required fields: user_id, room_id, booking_date, start_time, end_time
    Rate limited: 50 requests/hour
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
def api_update_booking(booking_id):
    """
    Update an existing booking.
    Users can update their own bookings, admins can update any booking.
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
def api_cancel_booking(booking_id):
    """
    Cancel a booking.
    Users can cancel their own bookings, admins can cancel any booking.
    """
    user_id, user_role = get_user_from_request()
    
    is_admin = user_role in ['Admin', 'Facility Manager']
    result = cancel_booking(booking_id, user_id, is_admin)
    
    if result.get('error'):
        status_code = 403 if 'Unauthorized' in result.get('error', '') else 400
        return jsonify(result), status_code
    
    return jsonify(result), 200


@booking_bp.route('/api/admin/bookings/<int:booking_id>/force-cancel', methods=['PUT'])
@log_request_response
def api_force_cancel_booking(booking_id):
    """
    Force cancel a booking (admin only).
    Allows admins to cancel any booking regardless of ownership.
    """
    user_id, user_role = get_user_from_request()
    
    if user_role != 'Admin':
        return jsonify({"error": "Unauthorized: Only admins can force cancel bookings"}), 403
    
    result = cancel_booking(booking_id, user_id, is_admin=True)
    
    if result.get('error'):
        return jsonify(result), 400
    
    # Log admin action
    if FEATURES_ENABLED:
        log_admin_action("Force cancelled booking", {"booking_id": booking_id})
    
    return jsonify(result), 200


@booking_bp.route('/api/admin/bookings/<int:booking_id>', methods=['PUT'])
def api_admin_update_booking(booking_id):
    """
    Admin update booking endpoint.
    Allows admins to override and update any booking.
    """
    user_id, user_role = get_user_from_request()
    
    if user_role != 'Admin':
        return jsonify({"error": "Unauthorized: Only admins can override bookings"}), 403
    
    booking_data = request.get_json()
    if not booking_data:
        return jsonify({"error": "No booking data provided"}), 400
    
    result = update_booking(booking_id, booking_data, user_id, is_admin=True)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@booking_bp.route('/api/admin/bookings/conflicts', methods=['GET'])
def api_get_conflicts():
    """
    Get conflicting bookings for a time slot (Admin only).
    Query parameters: room_id, date, start_time, end_time
    """
    user_id, user_role = get_user_from_request()
    
    if user_role != 'Admin':
        return jsonify({"error": "Unauthorized: Only admins can view conflicts"}), 403
    
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
def api_resolve_conflict(booking_id):
    """
    Resolve a booking conflict (Admin only).
    Body: {"action": "cancel" | "modify" | "override"}
    """
    user_id, user_role = get_user_from_request()
    
    if user_role != 'Admin':
        return jsonify({"error": "Unauthorized: Only admins can resolve conflicts"}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    action = data.get('action', 'cancel')
    result = resolve_booking_conflict(booking_id, action, user_id)
    
    if result.get('error'):
        return jsonify(result), 400
    
    return jsonify(result), 200


@booking_bp.route('/api/admin/bookings/stuck', methods=['GET'])
def api_get_stuck_bookings():
    """
    Get stuck bookings that need resolution (Admin only).
    """
    user_id, user_role = get_user_from_request()
    
    if user_role != 'Admin':
        return jsonify({"error": "Unauthorized: Only admins can view stuck bookings"}), 403
    
    stuck = get_stuck_bookings()
    return jsonify({"stuck_bookings": stuck, "count": len(stuck)}), 200


@booking_bp.route('/api/admin/bookings/<int:booking_id>/unblock', methods=['PUT'])
def api_unblock_booking(booking_id):
    """
    Unblock a stuck booking (Admin only).
    Body: {"action": "complete" | "cancel"}
    """
    user_id, user_role = get_user_from_request()
    
    if user_role != 'Admin':
        return jsonify({"error": "Unauthorized: Only admins can unblock bookings"}), 403
    
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
    Query parameter: service (optional) - 'users', 'rooms', 'bookings', 'reviews'
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
def api_reset_circuit_breaker(service_name):
    """
    Manually reset a circuit breaker (Admin only).
    """
    user_id, user_role = get_user_from_request()
    
    if user_role != 'Admin':
        return jsonify({"error": "Unauthorized: Only admins can reset circuit breakers"}), 403
    
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

