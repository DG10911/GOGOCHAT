import socket
import threading
import os
from protocol_utils import send_message, recv_message

HOST = '0.0.0.0'
PORT = 12345
BUFFER_SIZE = 4096

clients = {}
usernames = {}

def broadcast(sender, target, message):
    if target in clients:
        send_message(clients[target], f"MSG:{sender}:{message}")

def send_typing(sender, target):
    if target in clients:
        send_message(clients[target], f"TYPING:{sender} is typing...")

def handle_file_upload(sender, target, conn):
    try:
        metadata = recv_message(conn)  # filename|filesize
        if not metadata:
            return
        filename, fsize = metadata.split("|")
        fsize = int(fsize)

        file_bytes = b""
        while len(file_bytes) < fsize:
            chunk = conn.recv(min(BUFFER_SIZE, fsize - len(file_bytes)))
            if not chunk:
                break
            file_bytes += chunk

        if target in clients:
            send_message(clients[target], f"FILE:{sender}:{filename}:{fsize}")
            send_message(clients[target], f"{filename}|{fsize}")
            clients[target].sendall(file_bytes)
    except Exception as e:
        print(f"[File Error] {e}")

def handle_client(conn, addr):
    try:
        username = recv_message(conn)
        usernames[conn] = username
        clients[username] = conn
        print(f"[NEW CONNECTION] {username} connected from {addr}")

        while True:
            data = recv_message(conn)
            if not data:
                break

            if data.startswith("1TO1:"):
                _, target, msg = data.split(":", 2)
                broadcast(username, target, msg)

            elif data.startswith("TYPING:"):
                _, target = data.split(":", 1)
                send_typing(username, target)

            elif data.startswith("FILEUPLOAD:"):
                _, target = data.split(":", 1)
                handle_file_upload(username, target, conn)

    except Exception as e:
        print(f"[EXCEPTION] {e}")
    finally:
        uname = usernames.get(conn, "Unknown")
        print(f"[DISCONNECTED] {uname}")
        if uname in clients:
            del clients[uname]
        conn.close()

def start_server():
    print(f"[STARTING] Server running on {HOST}:{PORT}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()