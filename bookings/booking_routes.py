"""
Booking Routes
API endpoints for managing meeting room bookings.
"""
from flask import Blueprint, request, jsonify
from booking_model import (
    get_all_bookings,
    get_booking_by_id,
    get_user_bookings,
    get_room_bookings,
    check_room_availability,
    create_booking,
    update_booking,
    cancel_booking
)


booking_bp = Blueprint('booking_bp', __name__)


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
def api_get_all_bookings():
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
def api_create_booking():
    """
    Create a new booking.
    Regular users, Facility Managers can create bookings.
    Required fields: user_id, room_id, booking_date, start_time, end_time
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

