from flask import Flask
from flask_cors import CORS
from rooms_routes import room_bp

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(room_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
