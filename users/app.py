from flask import Flask, jsonify
from flask_cors import CORS
from user_routes import user_bp

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(user_bp)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint providing service information."""
    return jsonify({
        "service": "Users Service",
        "version": "1.0",
        "port": 5001,
        "status": "running",
        "endpoints": {
            "GET /admin/users": "Get all users",
            "GET /admin/users/<username>": "Get user by username",
            "POST /admin/users/add": "Add new user",
            "PUT /admin/user/update": "Update user",
            "DELETE /admin/users/delete/<username>": "Delete user",
            "PUT /admin/update/user_role": "Update user role",
            "PUT /api/admin/reset_password": "Reset password",
            "GET /regular_user/<user_name>": "Get regular user",
            "PUT /regular_user/update": "Update own profile",
            "GET /auditor/users": "Get all users (auditor)"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
