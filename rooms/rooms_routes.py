from flask import Blueprint, request, jsonify
from rooms_model import get_rooms, insert_room, get_room_by_name, update_room, delete_room

room_bp = Blueprint('room_bp', __name__)

@room_bp.route('/api/rooms', methods = ['GET'])
def api_get_rooms():
    return jsonify(get_rooms())

@room_bp.route('/api/rooms/<room_name>', methods=['GET'])
def get_room(room_name):
    return jsonify(get_room_by_name(room_name))

@room_bp.route('/rooms/add', methods = ['POST'])
def add_room():
    room = request.get_json()
    return jsonify(insert_room(room))

@room_bp.route('/api/rooms/update', methods=['PUT'])
def api_update_rooms():
    room = request.get_json()
    return jsonify(update_room(room))

@room_bp.route('/api/rooms/delete/<room_name>', methods=['DELETE'])
def delete_user(user_name):
    return jsonify(delete_user(user_name))