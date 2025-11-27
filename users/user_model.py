import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
import os

def connect_to_db():
    """
    Establishes a connection to the PostgreSQL database.
    
    Functionality:
        Creates a database connection using environment variables or default values.
        Uses RealDictCursor to return results as dictionaries instead of tuples.
    
    Parameters:
        None (uses environment variables):
            - DB_HOST: Database host (default: "db")
            - DB_NAME: Database name (default: "meetingroom")
            - DB_USER: Database user (default: "admin")
            - DB_PASSWORD: Database password (default: "password")
    
    Return value:
        psycopg2.connection: A database connection object with RealDictCursor factory.
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
    Retrieves all users from the database.
    
    Functionality:
        Fetches all user records from the Users table, returning only non-sensitive fields
        (user_id, user_name, username, email, user_role). Password hashes are excluded.
        Returns an empty list if an error occurs.
    
    Parameters:
        None
    
    Returns:
        list: A list of dictionaries containing all user records with fields:
            - user_id: Unique identifier for the user
            - user_name: Full name of the user
            - username: Username of the user
            - email: Email address of the user
            - user_role: Role of the user (e.g., "Admin", "Facility Manager", "regular user", "Auditor")
        Returns an empty list [] if an error occurs or the database is empty.
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
    Retrieves a single user by their username from the database.
    
    Functionality:
        Searches for a user with the specified username and returns their details.
        Returns only non-sensitive fields (password hash is excluded).
        Returns None if the user is not found or if an error occurs.
    
    Parameters:
        username (str): The username of the user to retrieve.
    
    Returns:
        dict or None: A dictionary containing the user record with fields:
            - user_id: Unique identifier for the user
            - user_name: Full name of the user
            - username: Username of the user
            - email: Email address of the user
            - user_role: Role of the user
        Returns None if the user is not found or if an error occurs.
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
    Inserts a new user into the database.
    
    Functionality:
        Creates a new user record in the Users table with the provided information.
        Automatically hashes the password before storing it in the database.
        Returns only non-sensitive fields (password hash is excluded from the response).
    
    Parameters:
        user (dict): A dictionary containing user information with the following keys:
            - user_name (str, required): Full name of the user
            - username (str, required): Unique username for the user
            - email (str, required): Email address of the user
            - password (str, required): Plain text password (will be hashed before storage)
            - user_role (str, required): Role of the user
    
    Returns:
        dict: A dictionary containing the newly created user record with fields:
            - user_id: Unique identifier for the user (auto-generated)
            - user_name: Full name of the user
            - username: Username of the user
            - email: Email address of the user
            - user_role: Role of the user
        Returns {"error": str, "details": str} dictionary if insertion fails
        (e.g., duplicate username, database constraint violation).
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
    Updates an existing user's information in the database.
    
    Functionality:
        Updates a user record identified by username_old with new values for user_name,
        username, email, and user_role. The username_old field is used to identify which
        user to update. Password is not updated by this function (use reset_password instead).
    
    Parameters:
        user (dict): A dictionary containing user information with the following keys:
            - username_old (str, required): Current username of the user to update (used as identifier)
            - user_name (str, required): New full name of the user
            - username (str, required): New username for the user
            - email (str, required): New email address of the user
            - user_role (str, required): New role of the user
    
    Returns:
        dict or None: A dictionary containing the updated user record with fields:
            - user_id: Unique identifier for the user
            - user_name: Full name of the user
            - username: Username of the user
            - email: Email address of the user
            - user_role: Role of the user
        Returns None if the user is not found or if an error occurs.
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
    Updates the role assigned to a specific user.
    
    Functionality:
        Changes only the user_role field for a user identified by username.
        All other user information remains unchanged.
    
    Parameters:
        username (str): The username of the user whose role will be updated.
        new_role (str): The new role to assign to the user.
    
    Returns:
        dict or None: A dictionary containing the updated user record with fields:
            - user_id: Unique identifier for the user
            - user_name: Full name of the user
            - username: Username of the user
            - email: Email address of the user
            - user_role: Updated role of the user
        Returns None if the user is not found or if an error occurs.
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
    Deletes a user from the database by their username.
    
    Functionality:
        Removes a user record from the Users table based on the username.
        Returns a success message if the user is found and deleted.
    
    Parameters:
        username (str): The username of the user to delete.
    
    Returns:
        dict or None: A dictionary with success message if deletion is successful:
            - message (str): "User deleted"
            - username (str): Username of the deleted user
        Returns None if the user is not found or if an error occurs.
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
    Resets a user's password in the database.
    
    Functionality:
        Updates the password_hash for a user identified by username.
        Automatically hashes the new password before storing it.
        Returns only non-sensitive fields (password hash is excluded from the response).
    
    Parameters:
        username (str): The username of the user whose password will be reset.
        new_password (str): The new plain text password (will be hashed before storage).
    
    Returns:
        dict or None: A dictionary containing the user record with fields:
            - user_id: Unique identifier for the user
            - user_name: Full name of the user
            - username: Username of the user
            - email: Email address of the user
            - user_role: Role of the user
        Returns None if the user is not found or if an error occurs.
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
    Allows a user to update their own profile information.
    
    Functionality:
        Updates a user's own profile information including user_name, email, and optionally password.
        The username field is used to identify which user to update.
        Password is optional - if provided, it will be hashed and updated; if not provided,
        the existing password hash is preserved.
    
    Parameters:
        user (dict): A dictionary containing user information with the following keys:
            - username (str, required): Username of the user to update (used as identifier)
            - user_name (str, required): New full name of the user
            - email (str, required): New email address of the user
            - password (str, optional): New plain text password (will be hashed if provided)
    
    Returns:
        dict or None: A dictionary containing the updated user record with fields:
            - user_id: Unique identifier for the user
            - user_name: Full name of the user
            - username: Username of the user
            - email: Email address of the user
            - user_role: Role of the user
        Returns None if the user is not found or if an error occurs.
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
    Authenticates a user by verifying their username and password.
    
    Functionality:
        Verifies the provided password against the stored password hash for the given username.
        Returns user information (excluding password hash) if authentication is successful.
        Returns different values to distinguish between user not found and incorrect password.
    
    Parameters:
        username (str): The username of the user attempting to log in.
        password (str): The plain text password entered by the user.
    
    Returns:
        dict, False, or None:
            - dict: A dictionary containing the user profile (if authentication successful) with fields:
                - user_id: Unique identifier for the user
                - user_name: Full name of the user
                - username: Username of the user
                - email: Email address of the user
                - user_role: Role of the user
            - None: If the user is not found in the database
            - False: If the user exists but the password is incorrect
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
    Retrieves the booking history for a specific user along with room details.
    
    Functionality:
        Fetches all bookings for a user identified by username, including associated room information.
        Results are ordered by booking date and start time (most recent first).
        Returns None if the user does not exist.
    
    Parameters:
        username (str): The username of the user whose booking history will be retrieved.
    
    Returns:
        list or None: A list of dictionaries containing booking records with fields:
            - booking_id: Unique identifier for the booking
            - booking_date: Date of the booking
            - start_time: Start time of the booking
            - end_time: End time of the booking
            - status: Status of the booking
            - room_name: Name of the booked room
            - room_location: Location of the booked room
            - Capacity: Capacity of the booked room
        Returns None if the user does not exist or if an error occurs.
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