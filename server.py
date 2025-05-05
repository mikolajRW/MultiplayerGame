import socket
import threading

BUFFER_SIZE = 1024
MAX_LOBBY = 4
HOST = ""
PORT = 61111
lobbies = {}

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    current_lobby = None
    try:
        while True:
            data = conn.recv(BUFFER_SIZE).decode()
            if not data:
                break

            print(f"Received from {addr}: {data}")

            if data.startswith("START"):
                lobby_id = str(len(lobbies) + 1)
                _, nickname = data.split(" ")
                lobbies[lobby_id] = [nickname]
             #   current_lobby = lobby_id
                print(nickname)
                conn.sendall(f"{1} {nickname}".encode())
            elif data.startswith("SHOW"):
                all_lobbies = ""
                for key, values in lobbies.items():
                    all_lobbies += f"{key}"
                    for value in values:
                        all_lobbies += f"-{value}"
                    all_lobbies += " "
                print(all_lobbies)
                conn.sendall(f"{all_lobbies}".encode())
            elif data.startswith("JOIN"):
                _, lobby_id, nickname = data.split(" ")
                if lobby_id in lobbies and len(lobbies[lobby_id]) < MAX_LOBBY:
                    lobbies[lobby_id].append(nickname)
                    print(lobbies)
                    conn.sendall("Joined".encode())
                else:
                    conn.sendall("Cannot join lobby".encode())
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection with {addr} closed.")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Server started on port {PORT}")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
