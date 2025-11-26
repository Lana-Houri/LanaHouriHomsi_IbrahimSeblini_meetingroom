import psycopg2
import psycopg2.extras
import os


def connect_to_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "meetingroom"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "password"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def ensure_room_status_constraint():
    """Allow legacy databases to accept 'Out-of-Service'."""
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
