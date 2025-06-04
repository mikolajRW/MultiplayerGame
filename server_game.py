import socket
import threading
import network_utils
import string
import random
from collections import defaultdict, Counter

# Setup
letters = [char for char in string.ascii_uppercase if char not in {'Q', 'X'}]
BUFFER_SIZE = 1024
HOST = ""
PORT = 61112
LOBBIES_ID = 0

# Shared state across threads
lobbies = {}
game_lock = threading.Lock()
letter_for_lobby = {}
answers_for_lobby = {}
data_to_verify = {}
compare_answers = {}
already_checked_answers = {}
rounds_per_lobby = {}
MAX_ROUNDS = 4
game_categories = ["Country", "City", "Animal", "Thing", "Occupation", "Movie"]
filepaths = ['dictionaries/countries.txt', 'dictionaries/cities.txt', 'dictionaries/animals.txt',
             'dictionaries/things.txt', 'dictionaries/occupations.txt', 'dictionaries/movies.txt']

# Send results to players and handle end of game
def handle_already_counted_points(conn, lobby_token):
    conn.sendall(f"SHOW_RESULTS-{letter_for_lobby[lobby_token]}-{answers_for_lobby[lobby_token]}".encode())
    already_checked_answers[lobby_token] += 1
    if already_checked_answers[lobby_token] == len(lobbies[lobby_token]):
        rounds_per_lobby[lobby_token] += 1
        if rounds_per_lobby[lobby_token] >= MAX_ROUNDS:
            # Send final scores and clean up
            leaderboard = "FINISH_GAME"
            for player_data in sorted(lobbies[lobby_token], key=lambda x: int(x[2]), reverse=True):
                leaderboard += f"-{player_data[1]}_{player_data[2]}"
            for player_data in lobbies[lobby_token]:
                player_data[0].sendall(leaderboard.encode())

            # Remove lobby data
            del lobbies[lobby_token]
            del rounds_per_lobby[lobby_token]
            del already_checked_answers[lobby_token]
            del answers_for_lobby[lobby_token]
        else:
            # Prepare for next round
            del already_checked_answers[lobby_token]
            del answers_for_lobby[lobby_token]

# Get nickname by matching connection
def get_nick_from_conn(lobby, conn):
    for val in lobby:
        if val[0].getpeername()[1] == conn.getpeername()[1]:
            return val[1]

# Load answer validation data from files
def get_data_to_verify_ans():
    for filepath, category in zip(filepaths, game_categories):
        with open(filepath, 'r') as file:
            data_to_verify[category] = {line.strip().lower() for line in file}

# Main message handler
def process_message_game(conn, message, addr):
    """
    Handles game-related commands for the 'Stop the Bus' multiplayer server.

    Commands:
        - CREATE_LOBBY <lobby_token> <nickname>
        - SHOW_PUNCTUATION <lobby_token>
        - LEAVE <lobby_token>
        - START_COUNTING <lobby_token>
        - GATHER_ANS <lobby_token> <answers>
        - CHECK_ANSWERS <lobby_token> <nickname>

    Parameters:
        conn (socket.socket): The client connection socket.
        message (str): The incoming message from the client.
        addr (tuple): The (IP, port) address of the client.

    Behavior:
        - Manages player connections and lobbies.
        - Validates answers against dictionaries.
        - Distributes random letters for each round.
        - Calculates and distributes scores.
        - Handles game state transitions (e.g., starting, leaving, finishing).
        - Ensures thread-safe access to shared game state.

    Exceptions:
        Logs and sends an error message to the client if processing fails.
    """

    try:
        if message.startswith("CREATE_LOBBY"):
            _, lobby_token, nickname = message.split(" ")
            with game_lock:
                if lobbies.get(lobby_token) is not None:
                    letter_for_lobby[lobby_token] = random.choice(letters)
                    lobbies[lobby_token].append([conn, nickname, '0'])
                else:
                    lobbies[lobby_token] = [[conn, nickname, '0']]
                    rounds_per_lobby[lobby_token] = 0
                conn.sendall("LOBBY CREATED".encode())

        elif message.startswith("SHOW_PUNCTUATION"):
            _, lobby_token = message.split(" ")
            with game_lock:
                players_points = 'SHOW_PUNCTUATION-' + letter_for_lobby[lobby_token]
                for player_data in lobbies[lobby_token]:
                    players_points += '-' + player_data[1] + '_' + player_data[2]
                conn.sendall(f"{players_points}".encode())

        elif message.startswith("LEAVE"):
            _, lobby_token = message.split(" ")
            with game_lock:
                for player_data in lobbies[lobby_token]:
                    if player_data[0] == conn and len(lobbies[lobby_token]) > 2:
                        lobbies[lobby_token].remove(player_data)
                        for player in lobbies[lobby_token]:
                            player[0].sendall("LEFT".encode())
                        break
                    elif player_data[0] == conn and len(lobbies[lobby_token]) <= 2:
                        for player in lobbies[lobby_token]:
                            player[0].sendall("FINISH_LOBBY".encode())
                        del lobbies[lobby_token]
                        del rounds_per_lobby[lobby_token]
                        break

        elif message.startswith("START_COUNTING"):
            _, lobby_token = message.split(" ")
            with game_lock:
                for player_data in lobbies[lobby_token]:
                    player_data[0].sendall("START_COUNTING".encode())
                conn.sendall("START_COUNTING".encode())

        elif message.startswith("GATHER_ANS"):
            _, lobby_token, answers = message.split(" ")
            with game_lock:
                answers = answers.split("-")
                ver_ans = []
                for ans in answers[:-1]:
                    ans = ans.split("_")
                    if ans[0].lower() in data_to_verify[ans[1]]:
                        ver_ans.append((ans[1], ans[0], conn))
                    else:
                        ver_ans.append((ans[1], "", conn))
                if compare_answers.get(lobby_token) is not None:
                    compare_answers[lobby_token].extend(ver_ans)
                else:
                    compare_answers[lobby_token] = ver_ans
                conn.sendall(f"CHECK_ANSWERS".encode())

        elif message.startswith("CHECK_ANSWERS"):
            _, lobby_token, nickname = message.split(" ")
            with game_lock:
                if already_checked_answers.get(lobby_token) is not None and already_checked_answers.get(lobby_token) > 0:
                    handle_already_counted_points(conn, lobby_token)
                    return

                # Tally points
                answers_for_lobby[lobby_token] = ''
                category_answer_counter = defaultdict(Counter)
                for category, answer, player_conn in compare_answers[lobby_token]:
                    if answer == "":
                        continue
                    category_answer_counter[category][answer.strip().lower()] += 1

                player_points = defaultdict(int)
                for category, answer, player_conn in compare_answers[lobby_token]:
                    if answer == "":
                        continue
                    normalized_answer = answer.strip().lower()
                    total_in_category = sum(category_answer_counter[category].values())
                    count = category_answer_counter[category][normalized_answer]

                    # Assign points based on uniqueness
                    if count == 1 and total_in_category == 1:
                        points = 15
                    elif count == 1:
                        points = 10
                    elif count > 1:
                        points = 5
                    else:
                        points = 0

                    answers_for_lobby[lobby_token] += f"{get_nick_from_conn(lobbies[lobby_token], player_conn)}_{category}_{answer}_{points}#"
                    player_points[player_conn.getpeername()[1]] += points

                del compare_answers[lobby_token]
                already_checked_answers[lobby_token] = 1

                # Update total points
                for player_data in lobbies[lobby_token]:
                    points_gained = player_points[player_data[0].getpeername()[1]]
                    points = int(player_data[2]) + points_gained
                    player_data[2] = str(points)

                # New letter for next round
                letter_for_lobby[lobby_token] = random.choice(letters)

                # Send results
                conn.sendall(f"SHOW_RESULTS-{letter_for_lobby[lobby_token]}-{answers_for_lobby[lobby_token]}".encode())

    except Exception as e:
        print(f"[PROCESSING ERROR] {addr}: {e}")
        conn.sendall(f"ERROR {e}\n".encode())

# Start the server
def start_server():
    get_data_to_verify_ans()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTED] Server running on port {PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=network_utils.handle_client, args=(conn, addr, BUFFER_SIZE, process_message_game), daemon=True)
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()