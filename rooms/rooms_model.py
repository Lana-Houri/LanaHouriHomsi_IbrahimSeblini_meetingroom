import psycopg2
import psycopg2.extras


def connect_to_db():
    return psycopg2.connect(
        host="db",
        database="meetingroom",
        user="admin",
        password="password",
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def get_rooms():
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Rooms ORDER BY room_id")
        return cur.fetchall()
    except Exception as e:
        print("get_rooms error:", e)
        return []
    finally:
        conn.close()

def get_room_by_name(room_name):
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Rooms WHERE room_name = %s", (room_name,))
        return cur.fetchone()
    except Exception as e:
        print("get_room_by_name error:", e)
        return None
    finally:
        conn.close()

def insert_room(room):
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
        conn.rollback()
        return None
    finally:
        conn.close()

def update_room(room):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE Rooms
            SET Capacity = %s,
                room_location = %s,
                equipment = %s,
                room_status = %s
            WHERE room_name = %s
            RETURNING room_id, room_name, Capacity, room_location, equipment, room_status
        """, (
            room["Capacity"],
            room["room_location"],
            room.get("equipment", None),
            room["room_status"],
            room["room_name"]
        ))

        conn.commit()
        return cur.fetchone()
    except Exception as e:
        print("update_room error:", e)
        conn.rollback()
        return None
    finally:
        conn.close()

def delete_room(room_name):
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
        conn.rollback()
        return None
    finally:
        conn.close()

def search_rooms(capacity=None, location=None, equipment=None):
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
        conn.close()
