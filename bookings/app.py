"""
Bookings Service Application
Service 3: Manages meeting room bookings and availability.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from booking_routes import booking_bp

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(booking_bp)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint providing service information."""
    return jsonify({
        "service": "Bookings Service",
        "version": "1.0",
        "port": 5002,
        "status": "running",
        "endpoints": {
            "GET /api/bookings": "Get all bookings (Admin/Facility Manager/Auditor)",
            "GET /api/bookings/<booking_id>": "Get specific booking",
            "GET /api/bookings/user/<user_id>": "Get user's booking history",
            "GET /api/bookings/room/<room_id>": "Get room bookings (optional ?date=YYYY-MM-DD)",
            "GET /api/bookings/availability": "Check room availability",
            "POST /api/bookings": "Create new booking",
            "PUT /api/bookings/<booking_id>": "Update booking",
            "PUT /api/bookings/<booking_id>/cancel": "Cancel booking",
            "PUT /api/admin/bookings/<booking_id>/force-cancel": "Force cancel (Admin)",
            "PUT /api/admin/bookings/<booking_id>": "Admin override booking"
        },
        "authentication": "Include X-User-ID and X-User-Role headers"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

