import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
import os

def connect_to_db():
    """
    Functionality: This function establish a PostgreSQL connection using environment configuration.

    Parameters: this function does not take any parameters.

    Value: This function returns a psycopg2 connection object configured with RealDictCursor.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "meetingroom"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "password"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def get_users():
    """
    Functionality: this function gets all the users from the database.

    Parameters: this function does not take any parameters.

    Value: This function will return a list of all the users presenet in the database. If there is an error or the database is empty, it will return an empty list.
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id, user_name, username, email, user_role FROM Users")
        return cur.fetchall()
    
    except Exception as e:
        print("get_users error:", e)
        return []
    
    finally:
        if conn:
            conn.close()


def get_user_by_username(username):
    """
    Functionality: This function gets the information on a specific user using the username.

    Parameters:
        - username: string identifier of the user to load.

    Value: returns the information of the user if the user exists and if not then it will return None.
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id, user_name, username, email, user_role FROM Users WHERE username = %s", (username,))
        return cur.fetchone()
    
    except Exception as e:
        print("get_user_by_username error:", e)
        return None
    
    finally:
        if conn:
            conn.close()

def insert_user(user):
    """
    Functionality: This function is used to create a new user and add it to the database after hashing the provided password. 

    Parameters:
        - user: which contains the user_name, the  username, the email, the  password and the user_role.

    Value: It will return the dictionary of the inserted row hence the information of the user added, or it will return an error dictionary on failure.
    """
    conn = None
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
        if conn:
            conn.rollback()
        return {"error": "Failed to insert user", "details": str(e)}
    
    finally:
        if conn:
            conn.close()

def update_user(user):
    """
    Functionality: this function update a users information including the user’s name, username, email, and role using username_old.

    Parameters:
        - user: for this parameter we need to pass a dictionary with new field values and 'username_old' to identify the record.

    Value: the information of the user will be printed using dictionary withthe updated row. If the update fails then it will return None.
    """
    conn = None
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
        if conn:
            conn.rollback()
        return None
    
    finally:
        if conn:
            conn.close()

def update_role(username, new_role):
    """
    Functionality: this function changes the role assigned to a certain user user.

    Parameters: We have 2 parameters for this function
        - username: string username to update.
        - new_role: string representing the desired role.

    Value: It will return dictionary of the user with the updated row. If it failes then it will return None.
    """
    conn = None
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
        if conn:
            conn.rollback()
        return None
    
    finally:
        if conn:
            conn.close()

def delete_user(username):
    """
    Functionality: This function will delete a user using their username.

    Parameters:
        - username: string username to be able to delete.

    Value: the function will print a dictionary with a confirmation message when deleted. And it didn't work it will print None.
    """
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("DELETE FROM Users WHERE username = %s RETURNING username", (username,))
        deleted = cur.fetchone()
        conn.commit()

        return {"message": "User deleted", "username": deleted['username']} if deleted else None
    
    except Exception as e:
        print("delete_user error:", e)
        if conn:
            conn.rollback()
        return None
    
    finally:
        if conn:
            conn.close()

def reset_password(username, new_password):
    """
    Functionality: This function will change the user’s password hash using the password provided.

    Parameters: It has 2 paramaters
        - username: string username whose password will change.
        - new_password: string password to hash and store in the db.

    Value: It will print the dictionary of the user and if if fails then it will return None.
    """
    conn = None
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
        if conn:
            conn.rollback()
        return None
    
    finally:
        if conn:
            conn.close()

def update_own_profile(user):
    """
    Functionality:This functiion allows a user to edit their own information such as their name, email, and password.

    Parameters:
        - user: it takes a dictionary containing username, user_name, email, and optional password.

    Value: the function will return a dictionary of the updated information of the user. If its unsuccessful it will return None. 
    """
    conn = None
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
        if conn:
            conn.rollback()
        return None
    
    finally:
        if conn:
            conn.close()


def login_user(username, password):
    """
    Functionality: this function will authenticate a user by verifying the provided password against the stored hash.

    Parameters: It takes 2 parameters
        - username: string username to authenticate.
        - password: string password entered by the user.

    Value: it will return a dictionary with the user profile when successful. And if the login wasn't successful because the user is missing then it will return None and if the password is invalid it will return false.
    """
    conn = None
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
        if conn:
            conn.close()

def get_booking_history(username):
    """
    Functionality: this function will retrieve the booking history for a specific user along with room details.

    Parameters:
        - username: string username whose bookings will be listed.

    Value: it will return a list of booking dictionaries. If the user doesn't exist then it will return None. 
    """
    conn = None
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
        if conn:
            conn.close()