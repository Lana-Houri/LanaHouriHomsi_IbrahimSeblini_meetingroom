"""
Example: Using Custom Error Handling
Demonstrates how to use the custom exception handling framework.
"""
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Flask, request, jsonify
from shared_utils.error_handler import (
    register_error_handlers,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    DatabaseError,
    ServiceUnavailableError,
    RateLimitError
)

app = Flask(__name__)

# Register error handlers
register_error_handlers(app)


@app.route('/api/example/validation', methods=['POST'])
def example_validation():
    """
    Example: Validation error.
    """
    data = request.get_json()
    
    if not data:
        raise ValidationError("Request body is required")
    
    if 'username' not in data:
        raise ValidationError("Username is required", field="username")
    
    if len(data.get('username', '')) < 3:
        raise ValidationError(
            "Username must be at least 3 characters",
            field="username",
            details={"min_length": 3}
        )
    
    return jsonify({"message": "Validation passed"})


@app.route('/api/example/auth', methods=['GET'])
def example_auth():
    """
    Example: Authentication error.
    """
    token = request.headers.get('Authorization')
    
    if not token:
        raise AuthenticationError("Authentication token is required")
    
    # Validate token (simulated)
    if token != "Bearer valid_token":
        raise AuthenticationError("Invalid authentication token")
    
    return jsonify({"message": "Authenticated"})


@app.route('/api/example/authorization', methods=['GET'])
def example_authorization():
    """
    Example: Authorization error.
    """
    user_role = request.headers.get('X-User-Role', 'regular user')
    
    if user_role != 'Admin':
        raise AuthorizationError(
            "Admin access required",
            required_role="Admin"
        )
    
    return jsonify({"message": "Authorized"})


@app.route('/api/example/not-found/<resource_id>', methods=['GET'])
def example_not_found(resource_id):
    """
    Example: Not found error.
    """
    # Simulate resource lookup
    resource_exists = False
    
    if not resource_exists:
        raise NotFoundError("Booking", resource_id=resource_id)
    
    return jsonify({"id": resource_id})


@app.route('/api/example/conflict', methods=['POST'])
def example_conflict():
    """
    Example: Conflict error.
    """
    data = request.get_json()
    room_id = data.get('room_id')
    booking_date = data.get('booking_date')
    
    # Simulate conflict check
    has_conflict = True
    
    if has_conflict:
        raise ConflictError(
            "Room is already booked for this time slot",
            conflict_type="booking_overlap",
            details={
                "room_id": room_id,
                "booking_date": booking_date
            }
        )
    
    return jsonify({"message": "Booking created"})


@app.route('/api/example/database', methods=['GET'])
def example_database():
    """
    Example: Database error.
    """
    # Simulate database error
    try:
        # database_operation()
        raise Exception("Connection timeout")
    except Exception as e:
        raise DatabaseError(
            "Failed to connect to database",
            details={"error": str(e)}
        )


@app.route('/api/example/service-unavailable', methods=['GET'])
def example_service_unavailable():
    """
    Example: Service unavailable error.
    """
    # Simulate service check
    service_available = False
    
    if not service_available:
        raise ServiceUnavailableError(
            service="Users Service",
            details={"retry_after": 60}
        )
    
    return jsonify({"message": "Service available"})


@app.route('/api/example/rate-limit', methods=['GET'])
def example_rate_limit():
    """
    Example: Rate limit error.
    """
    # Simulate rate limit check
    rate_limit_exceeded = True
    
    if rate_limit_exceeded:
        raise RateLimitError(
            "Rate limit exceeded. Please try again later.",
            retry_after=60,
            details={"limit": 100, "window": "hour"}
        )
    
    return jsonify({"message": "Request processed"})


if __name__ == '__main__':
    print("=== Error Handling Example ===")
    print("Start the Flask app and test the endpoints:")
    print("  POST /api/example/validation")
    print("  GET /api/example/auth")
    print("  GET /api/example/authorization")
    print("  GET /api/example/not-found/123")
    print("  POST /api/example/conflict")
    print("  GET /api/example/database")
    print("  GET /api/example/service-unavailable")
    print("  GET /api/example/rate-limit")
    app.run(debug=True, port=5004)

