"""
Reviews Service Application
Service 4: Handles room and service reviews from users.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from review_routes import review_bp

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(review_bp)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint providing service information."""
    return jsonify({
        "service": "Reviews Service",
        "version": "1.0",
        "port": 5003,
        "status": "running",
        "endpoints": {
            "GET /api/reviews": "Get all reviews (Admin/Moderator/Auditor)",
            "GET /api/reviews/<review_id>": "Get specific review",
            "GET /api/reviews/room/<room_id>": "Get reviews for a room",
            "GET /api/reviews/user/<user_id>": "Get user's reviews",
            "GET /api/reviews/flagged": "Get flagged reviews (Moderator/Admin)",
            "POST /api/reviews": "Submit new review",
            "PUT /api/reviews/<review_id>": "Update review",
            "DELETE /api/reviews/<review_id>": "Delete review",
            "POST /api/reviews/<review_id>/flag": "Flag review",
            "PUT /api/moderator/reviews/<review_id>/unflag": "Unflag review (Moderator/Admin)",
            "DELETE /api/moderator/reviews/<review_id>/remove": "Remove review (Moderator/Admin)",
            "PUT /api/admin/reviews/<review_id>": "Admin override review",
            "GET /api/auditor/reviews": "Get all reviews (Auditor)"
        },
        "authentication": "Include X-User-ID and X-User-Role headers"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

