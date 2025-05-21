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
                conn.sendall(f"{all_lobbies}".encode())
            elif data.startswith("LOBBY_SHOW"):
                _, lobby_id = data.split(" ")
                players_in_lobby = f"{lobby_id}"
                for value in lobbies[lobby_id]:
                    players_in_lobby += f"-{value}"
                    print(value)
                print(players_in_lobby)
                conn.sendall(f"{players_in_lobby}".encode())
            elif data.startswith("JOIN"):
                _, lobby_id, nickname = data.split(" ")
                if lobby_id in lobbies and len(lobbies[lobby_id]) <= MAX_LOBBY:
                    lobbies[lobby_id].append(nickname)
                    print(lobbies)
                    conn.sendall(f"Joined {lobby_id}".encode())
                else:
                    conn.sendall("Cannot join lobby".encode())
            elif data.startswith("LEAVE"):
                if current_lobby and nickname:
                    if current_lobby in lobbies:
                        if nickname in lobbies[current_lobby]:
                            lobbies[current_lobby].remove(nickname)
                            print(f"{nickname} left lobby {current_lobby}")

                            # If lobby is empty after leaving, remove it
                            if len(lobbies[current_lobby]) == 0:
                                del lobbies[current_lobby]
                                print(f"Lobby {current_lobby} removed (empty)")

                        conn.sendall("LEFT_SUCCESSFULLY".encode())
                        current_lobby = None
                        nickname = None
                    else:
                        conn.sendall("LOBBY_NOT_FOUND".encode())
                else:
                    conn.sendall("NOT_IN_LOBBY".encode())
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
