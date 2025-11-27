import psycopg2
import psycopg2.extras
import os


def connect_to_db():
    """
    Functionality:
    This function establishes a connection to the PostgreSQL database. 
    Its functionality is to create a database connection using environment variables.
    And it uses the RealDictCursor factory to return results as dictionaries instead of tuples.
    
    Parameters: None
    
    Returns: A database connection object.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "meetingroom"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "password"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def ensure_room_status_constraint():
    """
    Functionality:
    This function ensures the Rooms table has a constraint allowing 'Out-of-Service' status.
    If there exist any constraints on the room_status it will drop it and recreate it with the new constraint which is to include
    'Out-of-Service' as a valid status value.
    
    Parameters: None
    
    Returns: None
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("ALTER TABLE Rooms DROP CONSTRAINT IF EXISTS rooms_room_status_check")
        cur.execute(
            """
            ALTER TABLE Rooms
            ADD CONSTRAINT rooms_room_status_check
            CHECK (room_status IN ('Available', 'Booked', 'Out-of-Service'))
            """
        )
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print("ensure_room_status_constraint error:", e)
    finally:
        if conn:
            conn.close()

ensure_room_status_constraint()


def get_rooms():
    """
    Functionality: it gets all rooms that exists from the database.
    
    Parameters: None
    
    Returns: it will return a list of dictionaries containing all room records with fields which are:
    room_id, room_name, Capacity, room_location, equipment and room_status.
    In case of an error the function will return an empty list.
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Rooms ORDER BY room_id")
        return cur.fetchall()
    except Exception as e:
        print("get_rooms error:", e)
        return []
    finally:
        if conn:
            conn.close()

def get_room_by_name(room_name):
    """
    Retrieves a single room by its name from the database.
    
    Functionality:
        Searches for a room with the specified room_name and returns its details.
        Returns None if the room is not found or if an error occurs.
    
    Parameters:
        room_name (str): The name of the room to retrieve.
    
    Returns:
        dict or None: A dictionary containing the room record with fields:
            - room_id: Unique identifier for the room
            - room_name: Name of the room
            - Capacity: Maximum capacity of the room
            - room_location: Location of the room
            - equipment: Equipment available in the room (can be None)
            - room_status: Status of the room
        Returns None if the room is not found or if an error occurs.
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Rooms WHERE room_name = %s", (room_name,))
        return cur.fetchone()
    except Exception as e:
        print("get_room_by_name error:", e)
        return None
    finally:
        if conn:
            conn.close()

def insert_room(room):
    """
    Inserts a new room into the database.
    
    Functionality:
        Creates a new room record in the Rooms table with the provided information.
        Sets default room_status to 'Available' if not specified.
        Equipment is optional and defaults to None.
    
    Parameters:
        room (dict): A dictionary containing room information with the following keys:
            - room_name (str, required): Name of the room
            - Capacity (int, required): Maximum capacity of the room
            - room_location (str, required): Location of the room
            - equipment (str, optional): Equipment available in the room (defaults to None)
            - room_status (str, optional): Status of the room (defaults to "Available")
    
    Returns:
        dict or None: A dictionary containing the newly created room record with fields:
            - room_id: Unique identifier for the room (auto-generated)
            - room_name: Name of the room
            - Capacity: Maximum capacity of the room
            - room_location: Location of the room
            - equipment: Equipment available in the room
            - room_status: Status of the room
        Returns None if the insertion fails (e.g., duplicate room_name, database error).
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Rooms (room_name, Capacity, room_location, equipment, room_status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING room_id, room_name, Capacity, room_location, equipment, room_status
        """, (
            room["room_name"],
            room["Capacity"],
            room["room_location"],
            room.get("equipment", None),
            room.get("room_status", "Available")
        ))

        conn.commit()
        return cur.fetchone()
    except Exception as e:
        print("insert_room error:", e)
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def update_room(room):
    """
    Updates an existing room in the database.
    
    Functionality:
        Updates a room record identified by room_name with new values for Capacity,
        room_location, equipment, and room_status. Supports both "Capacity" and "capacity"
        as field names. All fields except equipment are required.
    
    Parameters:
        room (dict): A dictionary containing room information with the following keys:
            - room_name (str, required): Name of the room to update (used as identifier)
            - Capacity or capacity (int, required): Maximum capacity of the room
            - room_location (str, required): Location of the room
            - equipment (str, optional): Equipment available in the room (can be None)
            - room_status (str, required): Status of the room ('Available', 'Booked', or 'Out-of-Service')
    
    Returns:
        dict or None: A dictionary containing the updated room record with fields:
            - room_id: Unique identifier for the room
            - room_name: Name of the room
            - Capacity: Maximum capacity of the room
            - room_location: Location of the room
            - equipment: Equipment available in the room
            - room_status: Status of the room
        Returns None if the room is not found.
        Returns {"error": str} dictionary if required fields are missing or update fails.
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        capacity = room.get("Capacity") or room.get("capacity")
        room_location = room.get("room_location")
        equipment = room.get("equipment", None)
        room_status = room.get("room_status")
        room_name = room.get("room_name")

        if capacity is None:
            return {"error": "Missing required field: Capacity"}
        if room_location is None:
            return {"error": "Missing required field: room_location"}
        if room_status is None:
            return {"error": "Missing required field: room_status"}
        if room_name is None:
            return {"error": "Missing required field: room_name"}

        cur.execute("""
            UPDATE Rooms
            SET Capacity = %s,
                room_location = %s,
                equipment = %s,
                room_status = %s
            WHERE room_name = %s
            RETURNING room_id, room_name, Capacity, room_location, equipment, room_status
        """, (
            capacity,
            room_location,
            equipment,
            room_status,
            room_name
        ))

        conn.commit()
        result = cur.fetchone()
        
        if result is None:
            return None
        
        return result
    except KeyError as e:
        print("update_room missing field error:", e)
        if conn:
            conn.rollback()
        return {"error": f"Missing required field: {str(e)}"}
    except Exception as e:
        print("update_room error:", e)
        if conn:
            conn.rollback()
        return {"error": "Failed to update room", "details": str(e)}
    finally:
        if conn:
            conn.close()

def delete_room(room_name):
    """
    Deletes a room from the database by its name.
    
    Functionality:
        Removes a room record from the Rooms table based on the room_name.
        Returns a success message if the room is found and deleted.
    
    Parameters:
        room_name (str): The name of the room to delete.
    
    Returns:
        dict or None: A dictionary with success message if deletion is successful:
            - message (str): "Room deleted"
            - room_name (str): Name of the deleted room
        Returns None if the room is not found or if an error occurs.
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM Rooms WHERE room_name = %s RETURNING room_name",
            (room_name,)
        )

        deleted = cur.fetchone()
        conn.commit()

        if deleted:
            return {"message": "Room deleted", "room_name": deleted["room_name"]}
        return None
    except Exception as e:
        print("delete_room error:", e)
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def search_rooms(capacity=None, location=None, equipment=None):
    """
    Searches for rooms based on optional filter criteria.
    
    Functionality:
        Performs a flexible search on the Rooms table using one or more filter criteria.
        All parameters are optional and can be combined. Uses case-insensitive matching
        for location and equipment (ILIKE), and capacity filtering (>=).
    
    Parameters:
        capacity (int, optional): Minimum capacity requirement. Rooms with capacity >= this value will be returned.
        location (str, optional): Location filter. Rooms with room_location containing this string (case-insensitive) will be returned.
        equipment (str, optional): Equipment filter. Rooms with equipment containing this string (case-insensitive) will be returned.
    
    Returns:
        list: A list of dictionaries containing matching room records with fields:
            - room_id: Unique identifier for the room
            - room_name: Name of the room
            - Capacity: Maximum capacity of the room
            - room_location: Location of the room
            - equipment: Equipment available in the room
            - room_status: Status of the room
        Returns an empty list [] if no rooms match the criteria or if an error occurs.
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        query = "SELECT * FROM Rooms WHERE 1=1"
        params = []

        if capacity:
            query += " AND Capacity >= %s"
            params.append(capacity)

        if location:
            query += " AND room_location ILIKE %s"
            params.append(f"%{location}%")

        if equipment:
            query += " AND equipment ILIKE %s"
            params.append(f"%{equipment}%")

        cur.execute(query, tuple(params))
        return cur.fetchall()

    except Exception as e:
        print("search_rooms error:", e)
        return []
    finally:
        if conn:
            conn.close()
