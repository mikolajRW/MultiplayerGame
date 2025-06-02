"""
This is a multiplayer game server for a "Stop the Bus" (Polish: Państwa-Miasta)
Players can submit answers based on categories (like Country, City, Animal, etc.),
and receive points depending on how unique or correct their answers are.

Key features:
Lobby is created based on the lobby from the previous server - 'server_lobby.py' file
The server sends a random letter and players must give answers starting with that letter.
All answers are validated against category-specific dictionaries.
Points are awarded:
    15 points: if the answer is the only one in that category.
    10 points: if the answer is correct and unique but others also answered in that category.
    5 points: if the answer is a duplicate.
Players can leave lobbies, and lobbies close automatically when players leave.
Thread-safe handling of game state using locks.
"""


import socket
import threading
import network_utils
import string
import random
import pandas as pd
from collections import defaultdict, Counter

letters = [char for char in string.ascii_uppercase if char not in {'Q', 'X'}]
BUFFER_SIZE = 1024
HOST = ""
PORT = 61112
LOBBIES_ID = 0
# Shared lobby data and thread lock
lobbies = {}
game_lock = threading.Lock()
letter_for_lobby = {}
answers_for_lobby = {}
data_to_verify = {}
game_categories = ["Country", "City", "Animal", "Thing", "Occupation", "Movie"]
filepaths = ['dictionaries/countries.txt', 'dictionaries/cities.txt', 'dictionaries/animals.txt',
             'dictionaries/things.txt', 'dictionaries/occupations.txt', 'dictionaries/movies.txt']
compare_answers = {}
already_checked_answers = {}
ans = ''

def get_data_to_verify_ans():
    for filepath,category in zip(filepaths, game_categories):
        with open(filepath, 'r') as file:
            data_to_verify[category] = {line.strip().lower() for line in file}

def process_message_game(conn, message, addr):
    print(message)
    try:
        if message.startswith("CREATE_LOBBY"):
            _, lobby_token, nickname = message.split(" ")
            with game_lock:
                if lobbies.get(lobby_token) is not None:
                    letter_for_lobby[lobby_token] = random.choice(letters)
                    lobbies[lobby_token].append([conn,nickname,'0'])
                else:
                    lobbies[lobby_token] = [[conn, nickname,'0']]
                conn.sendall("LOBBY CREATED".encode())
        elif message.startswith("SHOW_PUNCTUATION"):
            _, lobby_token = message.split(" ")
            with game_lock:
                players_points = 'SHOW_PUNCTUATION-' + letter_for_lobby[lobby_token]
                for player_data in lobbies[lobby_token]:
                    players_points += '-'+player_data[1] + '_' + player_data[2]
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
                    conn.sendall(f"SHOW_RESULTS-{letter_for_lobby[lobby_token]}-{answers_for_lobby[lobby_token]}".encode())
                    already_checked_answers[lobby_token] += 1
                    if already_checked_answers[lobby_token] == len(lobbies[lobby_token]):
                        del already_checked_answers[lobby_token]
                        del answers_for_lobby[lobby_token]
                    return
                answers_for_lobby[lobby_token] = ''
                category_answer_counter = defaultdict(Counter)
                for category, answer, player_conn in compare_answers[lobby_token]:
                    if answer == "":
                        answers_for_lobby[lobby_token] += f"{nickname}_{category}_{answer}_0-"
                        continue
                    category_answer_counter[category][answer.strip().lower()] += 1
                print(category_answer_counter)
                player_points = defaultdict(int)

                for category, answer, player_conn in compare_answers[lobby_token]:
                    if answer == "":
                        continue
                    normalized_answer = answer.strip().lower()
                    total_in_category = sum(category_answer_counter[category].values())
                    count = category_answer_counter[category][normalized_answer]

                    if count == 1 and total_in_category == 1:
                        points = 15
                    elif count == 1:
                        points = 10
                    elif count > 1:
                        points = 5
                    else:
                        points = 0
                    answers_for_lobby[lobby_token] += f"{nickname}_{category}_{answer}_{points}-"
                    player_points[player_conn.getpeername()[1]] += points


                del compare_answers[lobby_token]
                already_checked_answers[lobby_token] = 1
                for player_data in lobbies[lobby_token]:
                    points_gained = player_points[player_data[0].getpeername()[1]]
                    points = int(player_data[2]) + points_gained
                    player_data[2] = str(points)
                letter_for_lobby[lobby_token] = random.choice(letters)
                print(answers_for_lobby)
                conn.sendall(f"SHOW_RESULTS-{letter_for_lobby[lobby_token]}-{answers_for_lobby[lobby_token]}".encode())
    except Exception as e:
        print(f"[PROCESSING ERROR] {addr}: {e}")
        conn.sendall(f"ERROR {e}\n".encode())

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
