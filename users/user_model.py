import psycopg2

def connect_to_db():
    return psycopg2.connect(
        host="db",
        database= "meetingroom",
        user="admin",
        password="password"
    )

def get_users(user):
    users= []
    try: 
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            """ SELECT * FROM Users"""
        ) 
        rows = cur.fetchall()

        for i in rows:
            user = {}
            user["user_id"] = i["user_id"]
            user["user_name"] = i ["user_name"]
            user["username"] = i ["username"]
            user["email"] = i ["email"]
            user["password_hash"] = i ["password_hash"]
            user["user_role"] = i ["user_role"]
            users.append(user)
    except:
        users = []
    return users

def get_user_by_name(username):
    user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Users WHERE user_name = %s", (username,)
        ) 
        row = cur.fetchone()
        user["user_id"] = row["user_id"]
        user["user_name"] = row["user_name"]
        user["username"] = row["username"]
        user["email"] = row["email"]
        user["password_hash"] = row["password_hash"]
        user["user_role"] = row["user_role"]
    except:
        user ={}
    return user
        

def insert_user(user):
    inserted_user = {}
    conn = connect_to_db()
    cur = conn.cursor()

    try:
        cur.execute("""
                INSERT INTO Users (user_name, username, email, password_hash, user_role) 
                    VALUES (?,?,?,?,?)""", user['user_name'], user['username'], user['email'], user['password_hash'], user['user_role']
                    )
        inserted_user = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
    
    finally:
        conn.close()
    
    return inserted_user

def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET user_name = %s, username = %s, email = %s, password_hash = %s, user_role = %s WHERE username = %s",
                    (user['user_name'], user['username'], user['email'], user['password_hash'], user['user_role'],)
        )
        conn.commit()
        updated_user = get_user_by_name(user["username"])

    except:
        conn.rollback()
        updated_user = {}

    finally:
        conn.close()

    return updated_user

def update_role(user):
    updated_user_role= {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET user_role = %s WHERE username = %s",
                    (user['user_role'], user['username'],)
        )
        updated_user_role = cur.fetchone()
        conn.commit()

    except:
        conn.rollback()
        updated_user_role = {}

    finally:
        conn.close()

    return updated_user_role

def delete_user(username):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE from users WHERE username= ?", (username,))
        conn.commit()
        message["status"] = "User deleted successfully"
    except:
        conn.rollback()
        message["status"] = "Cannot delete user"
    
    finally:
        conn.close()
    
    return message

from werkzeug.security import generate_password_hash

def reset_password(username, new_password):
    updated_user_pass = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        hashed_password = generate_password_hash(new_password)
        
        cur.execute("""
            UPDATE users
            SET password_hash = %s
            WHERE username = %s
            RETURNING user_id,user_name, username, email, user_role;
        """, (hashed_password, username))
        
        updated_user_pass = cur.fetchone()
        conn.commit()

    except:
        conn.rollback()
        updated_user_pass = {}

    finally:
        conn.close()

    return updated_user_pass

def update_own_profile(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        hashed_password = None

        if user.get('password_hash'):
            hashed_password = generate_password_hash(user['password'])

        cur.execute("""
            UPDATE users
            SET user_name = %s,
                email = %s,
                password_hash = COALESCE(%s, password_hash)
            WHERE username = %s
            RETURNING user_id, name, username, email, role, created_at;
        """, (user['user_name'], user['email'], hashed_password, user['username']))

        updated_user = cur.fetchone()
        conn.commit()

    except:
        conn.rollback()

    finally:
        conn.close()

    return updated_user

        
