"""
Lobby Server Module

This script sets up a TCP server that manages multiplayer game lobbies.
Clients can create, join, leave, and view lobbies. Once all players in a lobby are ready,
the server notifies them to start the game.

"""

# Import
import socket
import threading
import network_utils

# SERVER CONSTANTS
BUFFER_SIZE = 1024
HOST = ""
PORT = 61111

# GAME CONNECTED CONSTANTS
LOBBIES_ID = 0                     # Auto-incremented lobby ID
lobbies = {}                       # lobby_id -> list of client sockets
lobbies_ready = {}                # lobby_id -> count of ready players
lobby_lock = threading.Lock()     # Thread-safe lock for accessing shared data
MAX_LOBBY = 4


def process_message(conn: socket.socket, message: str, addr: tuple):
    """
    Processes a message received from a client.

    Handles various lobby-related commands:
        - START <nickname>
        - SHOW
        - LOBBY_SHOW <lobby_id>
        - JOIN <lobby_id> <nickname>
        - LEAVE <nickname> <lobby_id>
        - READY <nickname> <lobby_id>
        - UNREADY <nickname> <lobby_id>

    Parameters:
        conn (socket.socket): The client connection.
        message (str): The decoded message string from the client.
        addr (tuple): The (host, port) of the client.

    Behavior:
        - Manages shared lobby state with proper locking.
        - Sends responses to clients based on the current lobby state.
        - Notifies all clients in a lobby when all are ready to start.

    Exceptions:
        Prints and sends error messages if message parsing or lobby logic fails.
    """
    global LOBBIES_ID

    try:
        if message.startswith("START"):
            _, nickname = message.split(" ")
            with lobby_lock:
                lobby_id = str(LOBBIES_ID)
                LOBBIES_ID += 1
                lobbies[lobby_id] = [conn]
                lobbies_ready[lobby_id] = 0
            conn.sendall(f"{lobby_id}-{len(lobbies[lobby_id])}-{lobbies_ready[lobby_id]}\n".encode())

        elif message.startswith("SHOW"):
            response = ""
            with lobby_lock:
                for key, values in lobbies.items():
                    print(lobbies)
                    response += f"{key}"
                    for value in values:
                        response += f"-{value.getpeername()[1]}"
                    response += " "
            conn.sendall((response.strip() + "\n").encode())

        elif message.startswith("LOBBY_SHOW"):
            _, lobby_id = message.split(" ")
            with lobby_lock:
                if lobby_id in lobbies:
                    response = f"{lobby_id}-{len(lobbies[lobby_id])}-{lobbies_ready[lobby_id]}\n"
                else:
                    response = "LOBBY_NOT_FOUND\n"
            conn.sendall(response.encode())

        elif message.startswith("JOIN"):
            _, lobby_id, nickname = message.split(" ")
            with lobby_lock:
                if lobby_id in lobbies and len(lobbies[lobby_id]) < MAX_LOBBY:
                    lobbies[lobby_id].append(conn)
                    response = f"{lobby_id}-{len(lobbies[lobby_id])}-{lobbies_ready[lobby_id]}\n"
                    conn.sendall(response.encode())
                else:
                    conn.sendall("Cannot join lobby\n".encode())

        elif message.startswith("LEAVE"):
            _, nickname, lobby_id = message.split(" ")
            with lobby_lock:
                if lobby_id in lobbies and conn in lobbies[lobby_id]:
                    lobbies[lobby_id].remove(conn)
                    if len(lobbies[lobby_id]) == 0:
                        del lobbies[lobby_id]
                    conn.sendall("LEFT_SUCCESSFULLY\n".encode())
                else:
                    conn.sendall("NOT_IN_LOBBY\n".encode())

        elif message.startswith("READY"):
            _, nickname, lobby_id = message.split(" ")
            with lobby_lock:
                if len(lobbies[lobby_id]) <= 1:
                    conn.sendall(f"NOT-{lobby_id}-{len(lobbies[lobby_id])}".encode())
                else:
                    lobbies_ready[lobby_id] = lobbies_ready.get(lobby_id, 0) + 1
                    if len(lobbies[lobby_id]) - lobbies_ready[lobby_id] == 0:
                        for client in lobbies[lobby_id]:
                            client.send(f"START_GAME-{lobby_id}".encode())
                        conn.sendall(f"START_GAME-{lobby_id}".encode())
                        del lobbies[lobby_id]
                    else:
                        conn.sendall(f"{lobby_id}-{len(lobbies[lobby_id])}-{lobbies_ready[lobby_id]}".encode())

        elif message.startswith("UNREADY"):
            _, nickname, lobby_id = message.split(" ")
            if lobbies_ready[lobby_id] - 1 >= 0:
                lobbies_ready[lobby_id] -= 1
            conn.sendall(f"{lobby_id}-{len(lobbies[lobby_id])}-{lobbies_ready[lobby_id]}".encode())

        else:
            conn.sendall("UNKNOWN_COMMAND\n".encode())

    except Exception as e:
        print(f"[PROCESSING ERROR] {addr}: {e}")
        conn.sendall(f"ERROR {e}\n".encode())


def start_server():
    """
    Starts the lobby TCP server.

    - Binds to the configured HOST and PORT.
    - Accepts new client connections.
    - Spawns a new thread per client using `handle_client` from `network_utils`,
      passing the `process_message` function as a callback.

    This function blocks forever while the server is running.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[STARTED] Server running on port {PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(
            target=network_utils.handle_client,
            args=(conn, addr, BUFFER_SIZE, process_message),
            daemon=True
        )
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    start_server()
