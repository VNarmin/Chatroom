import socket
import threading
import mysql.connector
import json
from auth.chat_auth import authenticate_user, register_user
from client.chat_client import chat

clients = {}

def create_socket(port) :
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = '0.0.0.0'
    server_address = (host, port)
    s.bind(server_address)
    s.listen(5)
    print(f"Started listening on {host} : {port}")
    return s

def get_db_connection() :
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "root",
        database = "chatroom"
    )

def broadcast_message(message, room_ID) :
    for client_socket, client_info in clients.items() :
        if client_info['room_ID'] == room_ID :
            client_socket.send(message.encode('utf-8'))

def handle_registration(client_socket, username, password) :
    if register_user(username, password) :
        client_socket.send(json.dumps({"code" : 200, "username" : username, "message" : "Registration Successful!!"}).encode())
    else :
        client_socket.send(json.dumps({"code" : 400, "message" : "Registration Failed!!"}).encode())

def handle_login(client_socket, username, password) :
    if authenticate_user(username, password) :
        client_socket.send(json.dumps({"code" : 200, "username" : username, "message" : "Authentication Successful!!"}).encode())
    else :
        client_socket.send(json.dumps({"code" : 400, "message" : "Authentication Failed!!"}).encode())

def list_rooms() :
    conn = get_db_connection()
    cursor = conn.cursor(dictionary = True)
    cursor.execute("SELECT room_name, room_ID FROM rooms")
    rooms = cursor.fetchall()
    cursor.close()
    conn.close()
    return rooms

def join_room(client_socket, username, room_ID, room_password) :
    conn = get_db_connection()
    cursor = conn.cursor(dictionary = True)
    cursor.execute("SELECT * FROM rooms WHERE room_ID = %s AND room_password = %s", (room_ID, room_password))
    room = cursor.fetchone()
    cursor.close()
    conn.close()

    if room :
        clients[client_socket] = {'username' : username, 'room_ID' : room_ID}
        client_socket.send(json.dumps({"code" : 200, "message" : f"Joined room {room_ID}"}).encode())
        threading.Thread(target = chat, args = (client_socket, username), daemon = True).start()
    else :
        client_socket.send(json.dumps({"code" : 400, "message" : "Invalid room ID or password!!"}).encode())

def handle_create_room(client_socket, room_name, room_description, room_password) :
    conn = get_db_connection()
    cursor = conn.cursor()
    try :
        cursor.execute("INSERT INTO rooms (room_name, room_description, room_password) VALUES (%s, %s, %s)",
                       (room_name, room_description, room_password))
        conn.commit()
        client_socket.send(json.dumps({"code" : 200, "message" : "Room Creation Successful!!"}).encode())
    except mysql.connector.IntegrityError :
        client_socket.send(json.dumps({"code" : 400, "message" : "Room Creation Failed!!"}).encode())
    finally :
        cursor.close()
        conn.close()

def handle_delete_room(client_socket, room_ID) :
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rooms WHERE room_ID = %s", (room_ID,))
    conn.commit()
    if cursor.rowcount > 0 :
        client_socket.send(json.dumps({"code" : 200, "message" : "Room Deletion Successful!!"}).encode())
    else :
        client_socket.send(json.dumps({"code" : 400, "message" : "Room Deletion Failed!!"}).encode())
    cursor.close()
    conn.close()

def handle_client(client_socket) :
    username = None
    room_ID = None

    while True :
        action = client_socket.recv(1024).decode('utf-8')
        if not action : break

        data = json.loads(action)

        if data["action"] == "register" :
            username = data["username"]
            password = data["password"]
            handle_registration(client_socket, username, password)

        elif data["action"] == "login" :
            username = data["username"]
            password = data["password"]
            handle_login(client_socket, username, password)

        elif data["action"] == "join_room" :
            room_ID = data["room_ID"]
            room_password = data["room_password"]
            join_room(client_socket, username, room_ID, room_password)

        elif data["action"] == "create_room" :
            room_name = data["room_name"]
            room_description = data["room_description"]
            room_password = data["room_password"]
            handle_create_room(client_socket, room_name, room_description, room_password)

        elif data["action"] == "delete_room" :
            room_ID = data["room_ID"]
            handle_delete_room(client_socket, room_ID)

        elif data["action"] == "list" :
            rooms = list_rooms()
            client_socket.send(json.dumps({"rooms" : rooms}).encode())

        elif data["action"] == "send_message" :
            message_content = data["message"]
            if room_ID :
                formatted_message = f"{username} >> {message_content}"
                broadcast_message(formatted_message, room_ID)
        elif data["action"] == "disconnect" :
            print(f"{username} disconnected.")
            if client_socket in clients :
                del clients[client_socket]

def start_server() :
    server_socket = create_socket(3169)
    print("Server started, waiting for connections...")

    while True :
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        threading.Thread(target = handle_client, args = (client_socket,)).start()

if __name__ == "__main__" :
    try : start_server()
    except KeyboardInterrupt : print("\nBye\n")
    except Exception as e : print(f"Something went wrong! Shutting down...{e}")