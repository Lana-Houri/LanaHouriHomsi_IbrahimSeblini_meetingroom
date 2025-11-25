import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash

def connect_to_db():
    return psycopg2.connect(
        host="db",
        database="meetingroom",
        user="admin",
        password="password",
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def get_users():
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id, user_name, username, email, user_role FROM Users")
        return cur.fetchall()
    
    except Exception as e:
        print("get_users error:", e)
        return []
    
    finally:
        conn.close()


def get_user_by_username(username):
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id, user_name, username, email, user_role FROM Users WHERE username = %s", (username,))
        return cur.fetchone()
    
    except Exception as e:
        print("get_user_by_username error:", e)
        return None
    
    finally:
        conn.close()

def insert_user(user):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        hashed = generate_password_hash(user['password'])

        cur.execute("""
            INSERT INTO Users (user_name, username, email, password_hash, user_role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id, user_name, username, email, user_role
        """, (user['user_name'], user['username'], user['email'], hashed, user['user_role']))

        conn.commit()
        return cur.fetchone()
    
    except Exception as e:
        print("insert_user error:", e)
        conn.rollback()
        return None
    
    finally:
        conn.close()

def update_user(user):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE Users
            SET user_name = %s,
                username = %s,
                email = %s,
                user_role = %s
            WHERE username = %s
            RETURNING user_id, user_name, username, email, user_role
        """, (user['user_name'], user['username'], user['email'], user['user_role'], user['username_old']))

        conn.commit()
        return cur.fetchone()

    except Exception as e:
        print("update_user error:", e)
        conn.rollback()
        return None
    
    finally:
        conn.close()

def update_role(username, new_role):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE Users
            SET user_role = %s
            WHERE username = %s
            RETURNING user_id, user_name, username, email, user_role
        """, (new_role, username))

        conn.commit()
        return cur.fetchone()
    
    except Exception as e:
        print("update_role error:", e)
        conn.rollback()
        return None
    
    finally:
        conn.close()

def delete_user(username):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("DELETE FROM Users WHERE username = %s RETURNING username", (username,))
        deleted = cur.fetchone()
        conn.commit()

        return {"message": "User deleted", "username": deleted['username']} if deleted else None
    
    except Exception as e:
        print("delete_user error:", e)
        conn.rollback()
        return None
    
    finally:
        conn.close()

def reset_password(username, new_password):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        hashed = generate_password_hash(new_password)

        cur.execute("""
            UPDATE Users
            SET password_hash = %s
            WHERE username = %s
            RETURNING user_id, user_name, username, email, user_role
        """, (hashed, username))

        conn.commit()
        return cur.fetchone()
    
    except Exception as e:
        print("reset_password error:", e)
        conn.rollback()
        return None
    
    finally:
        conn.close()

def update_own_profile(user):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        new_hash = generate_password_hash(user['password']) if 'password' in user else None

        cur.execute("""
            UPDATE Users
            SET user_name = %s,
                email = %s,
                password_hash = COALESCE(%s, password_hash)
            WHERE username = %s
            RETURNING user_id, user_name, username, email, user_role
        """, (user['user_name'], user['email'], new_hash, user['username']))

        conn.commit()
        return cur.fetchone()
    
    except Exception as e:
        print("update_own_profile error:", e)
        conn.rollback()
        return None
    
    finally:
        conn.close()


def login_user(username, password):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT user_id, user_name, username, email, password_hash, user_role
            FROM Users
            WHERE username = %s
        """, (username,))
        
        user = cur.fetchone()
        if not user:
            return None

        if not check_password_hash(user['password_hash'], password):
            return False

        return {
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "username": user["username"],
            "email": user["email"],
            "user_role": user["user_role"]
        }

    except Exception as e:
        print("login_user error:", e)
        return None
    finally:
        conn.close()

def get_booking_history(username):
    try:
        conn = connect_to_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
        row = cur.fetchone()

        if not row:
            return None

        user_id = row["user_id"]

        cur.execute("""
            SELECT 
                b.booking_id,
                b.booking_date,
                b.start_time,
                b.end_time,
                b.status,
                r.room_name,
                r.room_location,
                r.Capacity
            FROM Bookings b
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE b.user_id = %s
            ORDER BY b.booking_date DESC, b.start_time DESC
        """, (user_id,))

        return cur.fetchall()

    except Exception as e:
        print("get_booking_history error:", e)
        return None
    finally:
        conn.close()


