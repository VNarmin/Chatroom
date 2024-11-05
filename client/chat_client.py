import socket
import json
import sys
import threading

def create_socket() :
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # creating a socket for TCP communication over IPv4
    server_address = ('localhost', 3169)
    s.connect(server_address)   # initiates a connection to the server
    return s

def register(client_sock) :
    username = input("Enter a username to register : ")
    password = input("Enter a password : ")
    action = {"action" : "register", "username" : username, "password" : password}
    client_sock.send(json.dumps(action).encode('utf-8'))
    register_response = client_sock.recv(1024).decode('utf-8')
    print("Registration Response : ", register_response)
    return json.loads(register_response)

def login(client_sock) :
    username = input("Enter your username : ")
    password = input("Enter your password : ")
    action = {"action" : "login", "username" : username, "password" : password}
    client_sock.send(json.dumps(action).encode('utf-8'))
    login_response = client_sock.recv(1024).decode('utf-8')
    print("Login Response : ", login_response)
    return json.loads(login_response)

def list_rooms(client_sock) :
    action = {"action" : "list"}
    client_sock.send(json.dumps(action).encode('utf-8'))
    list_rooms_response = client_sock.recv(1024).decode('utf-8')
    available_rooms = json.loads(list_rooms_response)["rooms"]
    print("\nAvailable Rooms : ")
    for room in available_rooms :
        print(f"Room : {room['room_name']}, ID : {room['room_ID']}")
    return available_rooms

def create_room(client_sock) :
    room_name = input("Enter the name of the new chatroom : ")
    room_description = input("Enter the description of the new chatroom : ")
    room_password = input("Enter the password of the new chatroom : ")
    action = {"action" : "create_room", "room_name" : room_name, "room_description" : room_description, "room_password" : room_password}
    client_sock.send(json.dumps(action).encode('utf-8'))
    create_response = client_sock.recv(1024).decode('utf-8')
    print("Create Room Response : ", create_response)

def delete_room(client_sock) :
    room_ID = input("Enter the ID of the chatroom to delete : ")
    action = {"action" : "delete_room", "room_ID" : room_ID}
    client_sock.send(json.dumps(action).encode('utf-8'))
    delete_response = client_sock.recv(1024).decode('utf-8')
    print("Delete Room Response : ", delete_response)

def join_room(client_sock) :
    room_ID = input("Enter a room ID to join : ")
    room_password = input("Enter the room password to join : ")
    action = {"action" : "join_room", "room_ID" : room_ID, "room_password" : room_password}
    client_sock.send(json.dumps(action).encode('utf-8'))
    join_response = client_sock.recv(1024).decode('utf-8')
    print("Join Room Response : ", join_response)
    return json.loads(join_response)

def listen_for_messages(client_sock) :
    while True :
        try :
            response = client_sock.recv(1024).decode('utf-8')
            if response :
                print(response)
            else : break
        except ConnectionAbortedError :
            print("Connection closed...")
            break

def chat(client_sock, username) :
    listen_thread = threading.Thread(target = listen_for_messages, args = (client_sock,), daemon = True)
    listen_thread.start()
    while True :
        message = input(f"{username} >> ")
        if message.lower() == 'quit' :
            action = {"action" : "disconnect"}
            client_sock.send(json.dumps(action).encode('utf-8'))
            print("You left the chatroom.")
            return
        action = {"action" : "send_message", "message" : message}
        client_sock.send(json.dumps(action).encode('utf-8'))

def clear_last_line():
    sys.stdout.write('\x1b[2K')
    sys.stdout.write('\r')
    sys.stdout.flush()

def main() :
    isAdmin = False
    current_username = None
    client_socket = create_socket()

    while True :
        if current_username is None :
            choice = input("Do you want to (r)egister or (l)ogin? ").lower()
            if choice == 'r' :
                registration_response = register(client_socket)
                if registration_response.get("code") == 200 :
                    current_username = registration_response.get("username")
            elif choice == 'l' :
                authentication_response = login(client_socket)
                if authentication_response.get("code") == 200 :
                    current_username = authentication_response.get("username")
                    isAdmin = (current_username == 'admin')
            else :
                print("Invalid Choice!!")
        else :
            command = input("\nEnter a command (list, create, delete, join, exit) : ").lower()
            if command == 'create' :
                if isAdmin :
                    create_room(client_socket)
                else :
                    print("Permission Denied. Only Admin!!")
            elif command == 'delete' :
                if isAdmin :
                    delete_room(client_socket)
                else :
                    print("Permission Denied. Only Admin!!")
            elif command == 'list' :
                list_rooms(client_socket)
            elif command == 'join' :
                join_resp = join_room(client_socket)
                if join_resp.get("code") == 200 :
                    chat(client_socket, current_username)
                    client_socket.close()
                    client_socket = create_socket()
            elif command == 'exit' :
                client_socket.close()
                print("Exiting...")
                break
            else :
                print("Invalid Command!!")

if __name__ == "__main__" :
    try :
        main()
    except KeyboardInterrupt :
        print("\nBye\n")
    except Exception as e :
        print(f"Something went wrong! Shutting down... {e}")