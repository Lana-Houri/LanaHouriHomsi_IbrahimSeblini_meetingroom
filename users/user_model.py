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
            """ SELECT * FROM Users WHERE user_name = ?"""
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

def get_user_by_name(user_name):
    user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Users WHERE user_name = %s", (user_name,)
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
        
