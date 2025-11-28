"""
Bookings Service Application
Service 3: Manages meeting room bookings and availability.
"""
import sys
import os

# Add parent directory to path for shared_utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Flask, jsonify
from flask_cors import CORS
from booking_routes import booking_bp
from datetime import time, date, datetime
import json

try:
    from shared_utils.rate_limiter import init_rate_limiter
    from shared_utils.audit_logger import setup_audit_logger
    FEATURES_ENABLED = True
except ImportError:
    print("WARNING: Shared utilities not found. Enhanced features disabled.")
    FEATURES_ENABLED = False

app = Flask(__name__)

# Custom JSON provider to handle time/date objects
from flask.json.provider import DefaultJSONProvider

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json = CustomJSONProvider(app)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize enhanced features if available
if FEATURES_ENABLED:
    limiter = init_rate_limiter(app)
    setup_audit_logger('bookings_audit.log')
    # Initialize limiter in blueprint
    from booking_routes import init_limiter
    init_limiter(limiter)
else:
    limiter = None

# Register blueprints
app.register_blueprint(booking_bp)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint providing service information."""
    features = []
    if FEATURES_ENABLED:
        features = ["Rate Limiting", "Audit Logging", "Circuit Breaker", "Encryption", "Secure Config"]
    
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
        "authentication": "Include X-User-ID and X-User-Role headers",
        "features": features
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
