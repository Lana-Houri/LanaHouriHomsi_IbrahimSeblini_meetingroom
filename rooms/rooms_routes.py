from flask import Blueprint, request, jsonify
from rooms_model import (
    get_rooms,
    insert_room,
    get_room_by_name,
    update_room,
    delete_room,
    search_rooms
)

room_bp = Blueprint("room_bp", __name__)

def get_user_role():
    return request.headers.get("X-User-Role", "regular user")

@room_bp.route("/api/rooms", methods=["GET"])
def api_get_rooms():
    return jsonify(get_rooms()), 200


@room_bp.route("/api/rooms/<room_name>", methods=["GET"])
def api_get_room(room_name):
    room = get_room_by_name(room_name)
    if not room:
        return jsonify({"error": "Room not found"}), 404
    return jsonify(room), 200


@room_bp.route("/api/rooms/search", methods=["GET"])
def api_search_rooms():
    capacity = request.args.get("capacity", type=int)
    location = request.args.get("location")
    equipment = request.args.get("equipment")

    rooms = search_rooms(capacity, location, equipment)
    return jsonify(rooms), 200


@room_bp.route("/api/rooms/available", methods=["GET"])
def api_get_available_rooms():
    rooms = get_rooms()
    available = [r for r in rooms if r["room_status"] == "Available"]
    return jsonify(available), 200


def require_admin_or_fm():
    role = get_user_role()
    if role not in ["Admin", "Facility Manager"]:
        return False
    return True


@room_bp.route("/rooms/add", methods=["POST"])
def api_add_room():
    if not require_admin_or_fm():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    result = insert_room(data)
    if not result:
        return jsonify({"error": "Insert failed"}), 400
    return jsonify(result), 201


@room_bp.route("/api/rooms/update", methods=["PUT"])
def api_update_room():
    if not require_admin_or_fm():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    result = update_room(data)
    if not result:
        return jsonify({"error": "Update failed"}), 400
    return jsonify(result), 200


@room_bp.route("/api/rooms/delete/<room_name>", methods=["DELETE"])
def api_delete_room(room_name):
    if not require_admin_or_fm():
        return jsonify({"error": "Unauthorized"}), 403

    result = delete_room(room_name)
    if not result:
        return jsonify({"error": "Room not found"}), 404
    return jsonify(result), 200


@room_bp.route("/api/rooms/toggle_status/<room_name>", methods=["PUT"])
def api_toggle_status(room_name):
    if not require_admin_or_fm():
        return jsonify({"error": "Unauthorized"}), 403

    room = get_room_by_name(room_name)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("room_status")
    
    if not new_status:
        current_status = room.get("room_status", "Available")
        new_status = "Booked" if current_status == "Available" else "Available"
    
    if new_status not in ["Available", "Booked"]:
        return jsonify({"error": f"Invalid status: '{new_status}'. Valid statuses are: 'Available', 'Booked'"}), 400

    room["room_status"] = new_status

    field_aliases = {
        "Capacity": ["Capacity", "capacity"],
        "room_location": ["room_location", "Room_location"],
        "room_name": ["room_name", "Room_Name"]
    }
    missing_fields = []
    for canonical, aliases in field_aliases.items():
        value_found = None
        for key in aliases:
            if key in room and room[key] is not None:
                value_found = room[key]
                break
        if value_found is None:
            missing_fields.append(canonical)
        else:
            room[canonical] = value_found

    if missing_fields:
        return jsonify({"error": f"Missing required fields in room data: {missing_fields}"}), 500
    
    updated = update_room(room)
    
    if updated is None:
        return jsonify({"error": "Room not found or update failed"}), 404
    
    if isinstance(updated, dict) and "error" in updated:
        return jsonify(updated), 500

    return jsonify(updated), 200

@room_bp.route("/facility_manager/rooms/out_of_service/<room_name>", methods=["PUT"])
def fm_mark_out_of_service(room_name):
    role = get_user_role()
    if role not in ["Facility Manager", "Admin"]:
        return jsonify({"error": "Unauthorized"}), 403

    room = get_room_by_name(room_name)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    room["room_status"] = "Out-of-Service"
    updated = update_room(room)

    if updated is None:
        return jsonify({"error": "Room not found or update failed"}), 404

    if isinstance(updated, dict) and "error" in updated:
        return jsonify(updated), 500

    return jsonify(updated), 200

@room_bp.route("/auditor/rooms", methods=["GET"])
def auditor_get_rooms():
    if get_user_role() != "Auditor":
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(get_rooms()), 200


@room_bp.route("/auditor/rooms/<room_name>", methods=["GET"])
def auditor_get_room(room_name):
    if get_user_role() != "Auditor":
        return jsonify({"error": "Unauthorized"}), 403

    room = get_room_by_name(room_name)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    return jsonify(room), 200
