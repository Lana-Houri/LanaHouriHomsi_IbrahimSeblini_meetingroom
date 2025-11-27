"""
Example: API Versioning Implementation
Demonstrates how to implement API versioning in routes.
"""
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Flask, jsonify, request
from shared_utils.api_versioning import (
    init_api_versioning,
    create_versioned_blueprint,
    get_api_version_manager
)

app = Flask(__name__)

# Initialize API versioning
init_api_versioning(
    default_version="v1",
    supported_versions=["v1", "v2"]
)

# Create versioned blueprints
v1_bp = create_versioned_blueprint("v1", "v1_api", __name__)
v2_bp = create_versioned_blueprint("v2", "v2_api", __name__)


# V1 Routes
@v1_bp.route('/bookings', methods=['GET'])
def get_bookings_v1():
    """
    V1 API: Get bookings (legacy format).
    """
    return jsonify({
        "version": "v1",
        "bookings": [
            {"id": 1, "room": "Room A", "date": "2024-01-15"}
        ],
        "format": "legacy"
    })


@v1_bp.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking_v1(booking_id):
    """
    V1 API: Get single booking.
    """
    return jsonify({
        "version": "v1",
        "booking": {
            "id": booking_id,
            "room": "Room A",
            "date": "2024-01-15"
        }
    })


# V2 Routes (enhanced)
@v2_bp.route('/bookings', methods=['GET'])
def get_bookings_v2():
    """
    V2 API: Get bookings (enhanced format with pagination).
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    return jsonify({
        "version": "v2",
        "data": {
            "bookings": [
                {"booking_id": 1, "room_name": "Room A", "booking_date": "2024-01-15"}
            ]
        },
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": 1
        },
        "format": "enhanced"
    })


@v2_bp.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking_v2(booking_id):
    """
    V2 API: Get single booking (enhanced format).
    """
    return jsonify({
        "version": "v2",
        "data": {
            "booking": {
                "booking_id": booking_id,
                "room": {
                    "room_id": 1,
                    "room_name": "Room A"
                },
                "booking_date": "2024-01-15",
                "time_slot": {
                    "start_time": "10:00:00",
                    "end_time": "11:00:00"
                }
            }
        }
    })


# Register blueprints
app.register_blueprint(v1_bp)
app.register_blueprint(v2_bp)


@app.route('/api/versions', methods=['GET'])
def get_supported_versions():
    """
    Get list of supported API versions.
    """
    version_manager = get_api_version_manager()
    return jsonify({
        "default_version": version_manager.default_version,
        "supported_versions": version_manager.supported_versions,
        "latest_version": version_manager.get_latest_version()
    })


if __name__ == '__main__':
    print("=== API Versioning Example ===")
    print("Test endpoints:")
    print("  GET /api/v1/bookings")
    print("  GET /api/v2/bookings")
    print("  GET /api/v1/bookings/1")
    print("  GET /api/v2/bookings/1")
    print("  GET /api/versions")
    print("\nVersion can be specified via:")
    print("  - URL path: /api/v1/... or /api/v2/...")
    print("  - Accept header: application/vnd.api.v1+json")
    print("  - X-API-Version header: v1 or v2")
    app.run(debug=True, port=5005)

