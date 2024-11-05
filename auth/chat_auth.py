import mysql.connector

def get_db_connection() :
    return (mysql.connector.connect (
        host = "localhost",
        user = "root",
        password = "root",
        database = "chatroom"
    ))

def register_user(username, password) :
    conn = get_db_connection()
    cursor = conn.cursor()
    try :
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return True  # registration successful
    except mysql.connector.IntegrityError :
        return False  # username already exists
    finally :
        cursor.close()
        conn.close()

def authenticate_user(username, password) :
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None  # returns True if username exists and password matches