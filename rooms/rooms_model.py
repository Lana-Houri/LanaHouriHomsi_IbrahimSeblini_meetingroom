import psycopg2

def connect_to_db():
    return psycopg2.connect(
        host="db",
        database= "meetingroom",
        user="admin",
        password="password"
    )


def get_rooms():
    rooms= []
    try: 
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            """ SELECT * FROM Rooms"""
        ) 
        rows = cur.fetchall()

        for i in rows:
            room = {}
            room["room_id"] = i["room_id"]
            room["room_name"] = i ["room_name"]
            room["Capacity"] = i ["Capacity"]
            room["room_location"] = i ["room_location"]
            room["room_status"] = i ["room_status"]
            rooms.append(room)
    except:
        rooms = []
    return rooms

def get_room_by_name(room_name):
    room = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Rooms WHERE room_name = %s", (room_name,)
        ) 
        row = cur.fetchone()
        room["room_id"] = row["room_id"]
        room["room_name"] = row["room_name"]
        room["Capacity"] = row["Capacity"]
        room["room_location"] = row["room_location"]
        room["room_status"] = row["room_status"]

    except:
        room ={}

    return room
        
def insert_room(room):
    inserted_room = {}
    conn = connect_to_db()
    cur = conn.cursor()

    try:
        cur.execute("""
                INSERT INTO Rooms (room_name, Capacity, room_location, room_status) 
                    VALUES (?,?,?,?)""", room['room_name'], room['Capacity'], room['room_location'], room['room_status']
                    )
        inserted_room = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
    
    finally:
        conn.close()
    
    return inserted_room


def update_room(room):
    updated_room = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE Rooms SET Capacity = %s, room_location = %s, room_status = %s WHERE room_name = %s",
                    (room['Capacity'], room['room_location'], room['room_status'],)
        )
        conn.commit()
        updated_room = get_room_by_name(room["room_name"])

    except:
        conn.rollback()
        updated_room = {}

    finally:
        conn.close()

    return updated_room


def delete_room(room_name):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE from Rooms WHERE room_name= ?", (room_name,))
        conn.commit()
        message["status"] = "Room deleted successfully"
    except:
        conn.rollback()
        message["status"] = "Cannot delete room"
    
    finally:
        conn.close()
    
    return message
        
