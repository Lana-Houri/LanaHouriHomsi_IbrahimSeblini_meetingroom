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
    """
    Retrieves the user role from the request headers.
    
    Functionality:
        Extracts the user role from the 'X-User-Role' header in the HTTP request.
        Returns a default role if the header is not present.
    
    Parameters:
        None (reads from Flask request.headers)
    
    Returns:
        str: The user role from the 'X-User-Role' header, or "regular user" if not present.
    """
    return request.headers.get("X-User-Role", "regular user")

@room_bp.route("/api/rooms", methods=["GET"])
def api_get_rooms():
    """
    API endpoint to retrieve all rooms.
    
    Functionality:
        Returns a list of all rooms in the database, ordered by room_id.
        No authentication required.
    
    Parameters:
        None (GET request with no query parameters)
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: List of room dictionaries, each containing:
                - room_id: Unique identifier for the room
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: Status of the room
            - Status code: 200 (OK)
    """
    return jsonify(get_rooms()), 200


@room_bp.route("/api/rooms/<room_name>", methods=["GET"])
def api_get_room(room_name):
    """
    API endpoint to retrieve a specific room by name.
    
    Functionality:
        Fetches a single room from the database using the room_name from the URL path.
        Returns 404 if the room is not found.
        No authentication required.
    
    Parameters:
        room_name (str): The name of the room to retrieve (from URL path parameter)
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: Room dictionary containing:
                - room_id: Unique identifier for the room
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: Status of the room
            - Status code: 200 (OK) if found, 404 (Not Found) if room doesn't exist
    """
    room = get_room_by_name(room_name)
    if not room:
        return jsonify({"error": "Room not found"}), 404
    return jsonify(room), 200


@room_bp.route("/api/rooms/search", methods=["GET"])
def api_search_rooms():
    """
    API endpoint to search for rooms using filter criteria.
    
    Functionality:
        Searches for rooms based on optional query parameters (capacity, location, equipment).
        All parameters are optional and can be combined. Uses case-insensitive matching
        for location and equipment, and minimum capacity filtering.
        No authentication required.
    
    Parameters:
        Query parameters (all optional):
            - capacity (int): Minimum capacity requirement
            - location (str): Location filter (case-insensitive partial match)
            - equipment (str): Equipment filter (case-insensitive partial match)
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: List of room dictionaries matching the search criteria, each containing:
                - room_id: Unique identifier for the room
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: Status of the room
            - Status code: 200 (OK)
    """
    capacity = request.args.get("capacity", type=int)
    location = request.args.get("location")
    equipment = request.args.get("equipment")

    rooms = search_rooms(capacity, location, equipment)
    return jsonify(rooms), 200


@room_bp.route("/api/rooms/available", methods=["GET"])
def api_get_available_rooms():
    """
    API endpoint to retrieve all available rooms.
    
    Functionality:
        Fetches all rooms from the database and filters to return only those
        with room_status set to "Available".
        No authentication required.
    
    Parameters:
        None (GET request with no query parameters)
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: List of available room dictionaries, each containing:
                - room_id: Unique identifier for the room
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: "Available"
            - Status code: 200 (OK)
    """
    rooms = get_rooms()
    available = [r for r in rooms if r["room_status"] == "Available"]
    return jsonify(available), 200


def require_admin_or_fm():
    """
    Checks if the current user has Admin or Facility Manager role.
    
    Functionality:
        Validates that the user role from request headers is either "Admin" or
        "Facility Manager". Used for authorization checks on protected endpoints.
    
    Parameters:
        None (reads from Flask request.headers via get_user_role())
    
    Returns:
        bool: True if user is Admin or Facility Manager, False otherwise.
    """
    role = get_user_role()
    if role not in ["Admin", "Facility Manager"]:
        return False
    return True


@room_bp.route("/rooms/add", methods=["POST"])
def api_add_room():
    """
    API endpoint to add a new room to the database.
    
    Functionality:
        Creates a new room record in the database. Requires Admin or Facility Manager role.
        Validates authorization before processing the request.
    
    Parameters:
        Request body (JSON, required):
            - room_name (str, required): Name of the room
            - Capacity (int, required): Maximum capacity of the room
            - room_location (str, required): Location of the room
            - equipment (str, optional): Equipment available in the room
            - room_status (str, optional): Status of the room (defaults to "Available")
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: Created room dictionary containing:
                - room_id: Unique identifier for the room (auto-generated)
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: Status of the room
            - Status code: 201 (Created) if successful, 403 (Forbidden) if unauthorized, 400 (Bad Request) if insertion fails
    """
    if not require_admin_or_fm():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    result = insert_room(data)
    if not result:
        return jsonify({"error": "Insert failed"}), 400
    return jsonify(result), 201


@room_bp.route("/api/rooms/update", methods=["PUT"])
def api_update_room():
    """
    API endpoint to update an existing room in the database.
    
    Functionality:
        Updates a room record identified by room_name with new values.
        Requires Admin or Facility Manager role. All fields except equipment are required.
        Supports both "Capacity" and "capacity" as field names.
    
    Parameters:
        Request body (JSON, required):
            - room_name (str, required): Name of the room to update (used as identifier)
            - Capacity or capacity (int, required): Maximum capacity of the room
            - room_location (str, required): Location of the room
            - equipment (str, optional): Equipment available in the room
            - room_status (str, required): Status of the room ('Available', 'Booked', or 'Out-of-Service')
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: Updated room dictionary containing:
                - room_id: Unique identifier for the room
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: Status of the room
            - Status code: 200 (OK) if successful, 403 (Forbidden) if unauthorized, 400 (Bad Request) if update fails
    """
    if not require_admin_or_fm():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    result = update_room(data)
    if not result:
        return jsonify({"error": "Update failed"}), 400
    return jsonify(result), 200


@room_bp.route("/api/rooms/delete/<room_name>", methods=["DELETE"])
def api_delete_room(room_name):
    """
    API endpoint to delete a room from the database.
    
    Functionality:
        Removes a room record from the database based on the room_name from the URL path.
        Requires Admin or Facility Manager role. Validates authorization before processing.
    
    Parameters:
        room_name (str): The name of the room to delete (from URL path parameter)
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: Success message dictionary containing:
                - message (str): "Room deleted"
                - room_name (str): Name of the deleted room
            - Status code: 200 (OK) if successful, 403 (Forbidden) if unauthorized, 404 (Not Found) if room doesn't exist
    """
    if not require_admin_or_fm():
        return jsonify({"error": "Unauthorized"}), 403

    result = delete_room(room_name)
    if not result:
        return jsonify({"error": "Room not found"}), 404
    return jsonify(result), 200


@room_bp.route("/api/rooms/toggle_status/<room_name>", methods=["PUT"])
def api_toggle_status(room_name):
    """
    API endpoint to toggle or set the status of a room between 'Available' and 'Booked'.
    
    Functionality:
        Updates the room_status of a room. If no status is provided in the request body,
        it toggles between 'Available' and 'Booked' (Available -> Booked, Booked -> Available).
        If a status is provided, it must be either 'Available' or 'Booked'.
        Requires Admin or Facility Manager role. Handles field name aliases for compatibility.
    
    Parameters:
        room_name (str): The name of the room to update (from URL path parameter)
        Request body (JSON, optional):
            - room_status (str, optional): Desired status ('Available' or 'Booked').
              If not provided, toggles from current status.
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: Updated room dictionary containing:
                - room_id: Unique identifier for the room
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: Updated status of the room
            - Status code: 200 (OK) if successful, 403 (Forbidden) if unauthorized,
              404 (Not Found) if room doesn't exist, 400 (Bad Request) if invalid status,
              500 (Internal Server Error) if missing required fields or update fails
    """
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
    """
    API endpoint for Facility Managers to mark a room as 'Out-of-Service'.
    
    Functionality:
        Sets the room_status of a room to 'Out-of-Service'. This is a specialized endpoint
        for Facility Managers and Admins to mark rooms as unavailable for maintenance or other reasons.
        Requires Facility Manager or Admin role.
    
    Parameters:
        room_name (str): The name of the room to mark as out of service (from URL path parameter)
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: Updated room dictionary containing:
                - room_id: Unique identifier for the room
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: "Out-of-Service"
            - Status code: 200 (OK) if successful, 403 (Forbidden) if unauthorized,
              404 (Not Found) if room doesn't exist, 500 (Internal Server Error) if update fails
    """
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
    """
    API endpoint for Auditors to retrieve all rooms.
    
    Functionality:
        Returns a list of all rooms in the database, ordered by room_id.
        This is a specialized endpoint for Auditors to view all room information.
        Requires Auditor role.
    
    Parameters:
        None (GET request with no query parameters)
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: List of room dictionaries, each containing:
                - room_id: Unique identifier for the room
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: Status of the room
            - Status code: 200 (OK) if successful, 403 (Forbidden) if unauthorized
    """
    if get_user_role() != "Auditor":
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(get_rooms()), 200


@room_bp.route("/auditor/rooms/<room_name>", methods=["GET"])
def auditor_get_room(room_name):
    """
    API endpoint for Auditors to retrieve a specific room by name.
    
    Functionality:
        Fetches a single room from the database using the room_name from the URL path.
        This is a specialized endpoint for Auditors to view specific room information.
        Requires Auditor role. Returns 404 if the room is not found.
    
    Parameters:
        room_name (str): The name of the room to retrieve (from URL path parameter)
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - JSON: Room dictionary containing:
                - room_id: Unique identifier for the room
                - room_name: Name of the room
                - Capacity: Maximum capacity of the room
                - room_location: Location of the room
                - equipment: Equipment available in the room
                - room_status: Status of the room
            - Status code: 200 (OK) if found, 403 (Forbidden) if unauthorized,
              404 (Not Found) if room doesn't exist
    """
    if get_user_role() != "Auditor":
        return jsonify({"error": "Unauthorized"}), 403

    room = get_room_by_name(room_name)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    return jsonify(room), 200
