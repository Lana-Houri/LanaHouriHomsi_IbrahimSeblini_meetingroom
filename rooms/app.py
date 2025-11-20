from flask import Flask, jsonify
from flask_cors import CORS
from rooms_routes import room_bp

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(room_bp)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint providing service information."""
    return jsonify({
        "service": "Rooms Service",
        "version": "1.0",
        "port": 5000,
        "status": "running",
        "endpoints": {
            "GET /api/rooms": "Get all rooms",
            "GET /api/rooms/<room_name>": "Get room by name",
            "POST /rooms/add": "Add new room",
            "PUT /api/rooms/update": "Update room",
            "DELETE /api/rooms/delete/<room_name>": "Delete room"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
