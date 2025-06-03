import time
from collections import defaultdict
from time import sleep

import pygame
import pandas as pd
import random
import string
import socket
import os
import threading
from itertools import islice
import time


MAX_LOBBY = 4
NUMBER_OF_CATEGORIES = 6
from pyexpat.errors import messages

# SET GLOBAL VARIABLES
pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
player = pygame.Rect((30, 250, 40, 40))
player_img = pygame.image.load("images/cursor.png")
player_img = pygame.transform.scale(player_img, (40, 40))
# player.x = 150

player_rect = player_img.get_rect(topleft=(30, 250))

category_color = (0, 50, 100)
answer_color = (255, 255, 255)
bg_color = (240, 230, 255)

game_font = pygame.font.Font(None, 50)
text_font = pygame.font.SysFont("Arial", 70)
results_font = pygame.font.Font(None, 36)  # Smaller font for results view

random_letter = random.choice(string.ascii_letters)

letters = [char for char in string.ascii_uppercase if char not in {'Q', 'X'}]

game_categories = ["Country", "City", "Animal", "Thing", "Occupation", "Movie"]
game_answers = [random.choice(letters)] * len(game_categories)
positions_x = [1.0] * len(game_categories)
positions_y = [1.0] * len(game_categories)
df = pd.DataFrame({"Category": game_categories, "Answer": game_answers, "PosX:": positions_x, "PosY": positions_y})
cursor = 0
run = True

HOST = "localhost"
PORT = 61111

class EstablishConnection:
    # Stores incoming messages from the server
    messages = []
    # Size of the buffer for receiving data
    BUFFER = 1024

    def listen(self):
        # Continuously listens for messages from the server
        while True:
            try:
                msg = self.client.recv(self.BUFFER).decode()
                # Save received message
                self.messages.append(msg)
            except:
                break

    def __init__(self, HOST, PORT):
        # Initialize connection to the server
        self.HOST = HOST
        self.PORT = PORT
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        self.client.connect((HOST, PORT))
        # Start listening in a background thread
        threading.Thread(target=self.listen, daemon=True).start()

    def send(self, data):
        # Sends data to the server
        try:
            self.client.sendall(data.encode())
        except Exception as e:
            print(f"Error - {e}")

    def get_latest_message(self):
        # Returns the most recent message received (or None if none)
        return self.messages[-1] if self.messages else None



class Game:
    def __init__(self):
        self.define_positions()
        self.menu(run, cursor, df)
        self.token = None



    def define_positions(self):
        for index in range(len(df)):
            if index < 3:
                df.at[index, "PosX"] = SCREEN_WIDTH / 20 + SCREEN_WIDTH / 4 * index
                df.at[index, "PosY"] = SCREEN_HEIGHT / 6
            else:
                df.at[index, "PosX"] = SCREEN_WIDTH / 20 + SCREEN_WIDTH / 4 * (index - 3)
                df.at[index, "PosY"] = SCREEN_HEIGHT / 1.7

    def print_categories_and_answers(self):
        for i in range(len(df)):
            self.draw_text(df.iloc[i]["Category"], game_font, category_color, df.iloc[i]["PosX"], df.iloc[i]["PosY"])
            self.draw_text(df.iloc[i]["Answer"], game_font, answer_color, df.iloc[i]["PosX"],
                      df.iloc[i]["PosY"] + SCREEN_HEIGHT / 8)

    def print_cursor(self,cursor_temp, game_array):
        screen.blit(player_img,
                    (game_array.iloc[cursor_temp]["PosX"], game_array.iloc[cursor_temp]["PosY"] + SCREEN_HEIGHT / 4.5))

    def check_cursor(self,cursor_f):
        if cursor_f < 0:
            cursor_f = 0
        elif cursor_f > len(game_categories) - 1:
            cursor_f -= 1

        return cursor_f


    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    def draw_pretty_text(self, text, font, text_col, bg_col, y, v_padding=8, h_padding=20, spacing=4, prev_rect=None):

        text_surface = font.render(text, True, text_col)
        text_rect = text_surface.get_rect()

        bar_height = text_rect.height + 2 * v_padding
        bar_width = SCREEN_WIDTH - 2 * h_padding

        if prev_rect:
            y = max(y, prev_rect.bottom + spacing)

        bar_rect = pygame.Rect(h_padding, y - bar_height // 2, bar_width, bar_height)

        if bg_col:
            pygame.draw.rect(screen, bg_col, bar_rect, border_radius=5)

        text_rect.center = bar_rect.center
        screen.blit(text_surface, text_rect)

        return bar_rect


    def menu(self, run, cursor, df):

        create_lobby_button = Button(width=SCREEN_WIDTH / 2, height=SCREEN_HEIGHT / 5, text="New Lobby",
                                     font=text_font, text_col=(100, 100, 100), x=SCREEN_WIDTH / 2 - SCREEN_WIDTH / 4,
                                     y=SCREEN_HEIGHT - SCREEN_HEIGHT / 1.5)
        join_lobby_button = Button(width=SCREEN_WIDTH / 2, height=SCREEN_HEIGHT / 5, text="Show Lobbies",
                                   font=text_font, text_col=(100, 100, 100), x=SCREEN_WIDTH / 2 - SCREEN_WIDTH / 4,
                                   y=SCREEN_HEIGHT - SCREEN_HEIGHT / 2.5)
        # exit_button = draw_text("EXIT", text_font, (255, 255, 255), SCREEN_WIDTH/2, SCREEN_HEIGHT/1.8)
        buttons = [join_lobby_button, create_lobby_button]

        while run:
            screen.fill((235, 132, 250))
            menu_text = text_font.render("Menu", True, (0, 0, 0))
            text_react = menu_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 10))
            screen.blit(menu_text, text_react)

            for button in buttons:
                button.draw(screen)

            key = pygame.key.get_pressed()
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if create_lobby_button.checkForClick(mouse):
                        self.lobby_type = "START"
                        self.enter_data(cursor)
                    if join_lobby_button.checkForClick(mouse):
                        self.lobby_type = "SHOW"
                        self.enter_data(cursor)
                if event.type == pygame.MOUSEMOTION:
                    for button in buttons:
                        button.change_color(mouse)

            cursor = self.check_cursor(cursor)
            pygame.display.update()
            pygame.display.flip()


    def enter_data(self, cursor):
        self.nickname = ""
        nickname_button = Button(width=SCREEN_WIDTH / 2, height=SCREEN_HEIGHT / 5, text=self.nickname,
                                 font=text_font, text_col=(100, 100, 100),
                                 x=SCREEN_WIDTH / 2 - SCREEN_WIDTH / 4,
                                 y=SCREEN_HEIGHT - SCREEN_HEIGHT / 2)
        lobby_button = Button(width=SCREEN_WIDTH / 4, height=SCREEN_HEIGHT / 5, text=self.lobby_type,
                              font=text_font, text_col=(100, 100, 100),
                              x=SCREEN_WIDTH / 4 - SCREEN_WIDTH / 8,
                              y=SCREEN_HEIGHT - SCREEN_HEIGHT / 4)
        buttons = [nickname_button, lobby_button]
        while run:
            screen.fill((235, 132, 250))
            nickname_text = text_font.render("Enter Nickname", True, (0, 0, 0))
            nickname_rect = nickname_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 10))
            screen.blit(nickname_text, nickname_rect)
            mouse = pygame.mouse.get_pos()

            nickname_button.text = self.nickname if self.nickname else "Enter Nickname"

            for button in buttons:
                button.draw(screen)
            key = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.menu(run, cursor, df)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if lobby_button.checkForClick(mouse=pygame.mouse.get_pos()):
                        self.create_lobby()
                if event.type == pygame.KEYDOWN:
                    if event.unicode.isalpha() or event.unicode.isspace() or event.unicode.isdigit():
                        if self.nickname == "Enter Nickname":
                            self.nickname = event.unicode
                        else:
                            self.nickname += event.unicode
                    elif event.key == pygame.K_BACKSPACE and self.nickname != "Enter Nickname":
                        self.nickname = self.nickname[:-1]
                        if len(self.nickname) == 0:
                            self.nickname = "Enter Nickname"
                    else:
                        print("Wrong Input")
                if event.type == pygame.MOUSEMOTION:
                    for button in buttons:
                        button.change_color(mouse)
            cursor = self.check_cursor(cursor)
            pygame.display.update()
            pygame.display.flip()


    def set_buttons_in_lobby(self):
        exit_button = Button(
            width=SCREEN_WIDTH / 4,
            height=SCREEN_HEIGHT / 10,
            text="Exit Lobby",
            font=game_font,
            text_col=(100, 100, 100),
            x=SCREEN_WIDTH / 2 - SCREEN_WIDTH / 4,
            y=SCREEN_HEIGHT - SCREEN_HEIGHT / 4
        )

        # Button resposnbile for refreshing lobby
        refresh_button_lobbies = Button(
            width=SCREEN_WIDTH / 4,
            height=SCREEN_HEIGHT / 10,
            text="Refresh",
            font=game_font,
            text_col=(100, 100, 100),
            x=SCREEN_WIDTH - SCREEN_WIDTH / 4 - 20,
            y=450
        )

        refresh_button_lobby = Button(
            width=SCREEN_WIDTH / 4,
            height=SCREEN_HEIGHT / 10,
            text="Refresh",
            font=game_font,
            text_col=(100, 100, 100),
            x=SCREEN_WIDTH / 15,
            y=525
        )

        ready_button = Button(
            width=SCREEN_WIDTH / 4,
            height=SCREEN_HEIGHT / 10,
            text="READY",
            font=game_font,
            text_col=(100, 100, 100),
            x=SCREEN_WIDTH / 1.5 - SCREEN_WIDTH / 7,
            y=SCREEN_HEIGHT - SCREEN_HEIGHT / 4
        )

        return exit_button, refresh_button_lobbies, refresh_button_lobby, ready_button

    def leaving_lobby(self, last_msg, connection):
        """
        Sends a LEAVE message to the server when a player exits a lobby.
        Determines the lobby number from the last received message and closes the network connection.
        Then, returns the player to the main menu.
        """
        # we send information to server - self.nickname - nickname of player, lobby_number - lobby in which player was
        if last_msg[0] == "NOT":
            lobby_number = last_msg[1]
            connection.send(f"LEAVE {self.nickname} {lobby_number}\n")
        else:
            lobby_number = last_msg[0]
            connection.send(f"LEAVE {self.nickname} {lobby_number}\n")

        # Envoke function responsible for closing connection
        self.close_network_connection(connection, "LEAVING")
        self.menu(run, cursor, df)

    def joining_lobby(self, join_button_dict, connection):
        for key, value in islice(join_button_dict.items(), 1, None):
            if value is not None and value.checkForClick(pygame.mouse.get_pos()):
                self.lobby_type = "LOBBY_SHOW"
                lobby_id = key.split('_')[2]
                connection.send(f"JOIN {lobby_id} {self.nickname}\n")
                # Check for response immediately after sending JOIN
                last_msg = str(connection.get_latest_message()).split(" ")
                if last_msg[0] == "ERROR_NICKNAME_TAKEN":
                    self.draw_pretty_text("Nickname already taken! Choose another.", game_font, (255, 0, 0), bg_color, 50)
                    pygame.display.update()
                    pygame.time.delay(2000)
                    self.close_network_connection(connection, "Nickname taken, returning to nickname input")
                    self.enter_data(cursor)
                    break


    def handle_readiness_for_game(self, last_msg, connection, message):
        prev_error = 0
        if last_msg[0] == "NOT":
            prev_error = 1
        connection.send(f"{message} {self.nickname} {last_msg[0 + prev_error]}\n")


    def present_available_lobbies(self, last_msg, active_buttons, refresh_button_lobbies, join_button_dict, pos):
        """
            Displays a list of available lobbies on the screen.
            For each lobby, shows its ID and number of players, and adds a 'join' button next to it.

            Returns updated join_button_dict, active_buttons list, new vertical position, and in_lobby flag.
        """

        in_lobby = False
        last_rect = None
        # Add the refresh button to the list of interactive buttons
        active_buttons.append(refresh_button_lobbies)
        for msg in last_msg:
            if msg == '\n' or msg is None:
                continue

            # Split message into lobby info and player names
            msg = msg.split("-")

            # Display the lobby info: ID and number of players
            last_rect = self.draw_pretty_text(F"Lobby ID: {msg[0]}, amount of players: {len(msg) - 1}/{MAX_LOBBY}",
                                              game_font, category_color, bg_color, pos, 8, 10, last_rect)

            # Create dynamic variable to properly named buttons in the join_button_dictionary
            var_name = f"join_button_{msg[0]}"

            join_button_dict[var_name] = Button(width=SCREEN_WIDTH / 25, height=SCREEN_HEIGHT / 25, text="",
                                                font=text_font, text_col=(100, 100, 100),
                                                x=SCREEN_WIDTH / 10 + SCREEN_WIDTH / 1.25,
                                                y=pos)

            # Add the join button to the list of interactive buttons
            active_buttons.extend([join_button_dict[var_name]])
            pos += 50
        return join_button_dict, active_buttons, pos, in_lobby



    def situation_in_lobby(self, last_msg, pos, last_rect):
        """
        This function displays information about:
        - How many players are in lobby
        - How many players are ready to start a game
        - If there is only one player - he cannot start a game - to little players to play
        """
        if last_msg[0] == "NOT":
            last_rect = self.draw_pretty_text(F"Lobby ID: {last_msg[1]}, amount of players: {last_msg[2]}/{MAX_LOBBY}",
                                              game_font, category_color, bg_color, pos, 8, 20, 28, last_rect)
            last_rect = self.draw_pretty_text("Not enough players to start a game", game_font, category_color,
                                              bg_color, pos + 50, 8, 20, prev_rect=last_rect)
        else:
            last_rect = self.draw_pretty_text(F"Lobby ID: {last_msg[0]}, amount of players: {last_msg[1]}/{MAX_LOBBY}",
                                              game_font, category_color, bg_color, pos, prev_rect=last_rect)
            last_rect = self.draw_pretty_text(f"{last_msg[-1][0]}/{last_msg[1]} READY", game_font, category_color,
                                              bg_color, pos + 50, prev_rect=last_rect)

        return last_rect

    def create_lobby(self):
        """
        Handles the main logic for creating, joining, and interacting with game lobbies.

        This function runs the lobby screen loop, managing player inputs (like joining, refreshing, or exiting lobbies),
        updates lobby state based on server responses, and transitions to gameplay when all players are ready.

        It also updates UI elements like lobby lists, player readiness status, and active buttons.
        """

        HOST = "localhost"
        PORT = 61111
        connection = EstablishConnection(HOST, PORT)

        # If player wants to start his own lobby - flag self.lobby_type = "START
        if self.lobby_type == "START":
            connection.send(f"{self.lobby_type} {self.nickname}\n")
        # If player want to join lobby - we show him all available lobbies
        elif self.lobby_type == "SHOW":
            connection.send(f"{self.lobby_type}\n")

        '''
        Buttons in lobby:
        exit_button - responsible for leaving a lobby
        refresh_button_lobbies - used in a situation when player wants to show what lobbies are open
        refresh_button_lobby - used in a salutation when player is in lobby, and this player wants to see changes in his lobby
        ready_button - if player is ready to play a game
        '''
        exit_button, refresh_button_lobbies, refresh_button_lobby, ready_button = self.set_buttons_in_lobby()



        # if player is already in lobby - exit_button is available
        in_lobby = False

        # lists which store every button used in this view
        active_buttons = []

        # dictionary of buttons which are visible during 'self.lobby_type' = show - allows player to join particular lobby
        join_button_dict = {}

        # flag which controls if player wants to join lobby with to many players
        cannot_join_lobby = False
        while run:

            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():

                # If player clicks 'Quit' on a screen he leaves lobby
                if event.type == pygame.QUIT:
                    self.leaving_lobby(last_msg, connection)

                if event.type == pygame.MOUSEBUTTONDOWN:

                    # Function handling joining lobby
                    self.joining_lobby(join_button_dict, connection)

                    # Button responsible for leaving a lobby
                    if exit_button is not None and exit_button.checkForClick(pygame.mouse.get_pos()):
                        self.leaving_lobby(last_msg, connection)

                    # Player clicks 'refresh_button_lobbies' button - wants to upload newly created lobbies
                    if refresh_button_lobbies is not None and refresh_button_lobbies.checkForClick(pygame.mouse.get_pos()):
                        connection.send(f"SHOW\n")

                    # If players click that he is ready for joining the game - click 'READY' button
                    if ready_button is not None and ready_button.checkForClick(pygame.mouse.get_pos()) and ready_button.get_text() == "READY":
                        self.handle_readiness_for_game(last_msg, connection, "READY")
                        ready_button.set_text("UNREADY")
                    # If players wants to change his readyness - click 'UNREADY' button
                    elif ready_button is not None and ready_button.checkForClick(pygame.mouse.get_pos()) and ready_button.get_text() == "UNREADY":
                        self.handle_readiness_for_game(last_msg, connection,"UNREADY")
                        ready_button.set_text("READY")
                    # Refresh changes in a lobby - if any player joined the game or change his readiness
                    if refresh_button_lobby is not None and refresh_button_lobby.checkForClick(pygame.mouse.get_pos()):
                        prev_error = 0
                        if last_msg[0] == "NOT":
                            prev_error = 1
                        connection.send(f"LOBBY_SHOW {last_msg[0 + prev_error]}\n")

                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and in_lobby:
                    if ready_button is not None and ready_button.get_text() == "READY":
                        self.handle_readiness_for_game(last_msg, connection, "READY")
                        ready_button.set_text("UNREADY")
                    elif ready_button is not None and ready_button.get_text() == "UNREADY":
                        self.handle_readiness_for_game(last_msg, connection, "UNREADY")
                        ready_button.set_text("READY")

                # If mouse is over the button - the color of button changes
                if event.type == pygame.MOUSEMOTION:
                    for button in active_buttons:
                        button.change_color(mouse)


            screen.fill((235, 132, 250))
            pos = 50

            # Last message from the server
            last_msg = str(connection.get_latest_message()).split(" ")

            # Reset 'active_buttons' list in every iteration - to check changes
            active_buttons = []

            # If we are in the lobby 'exit_button' is available
            if in_lobby:
                active_buttons.extend([exit_button])
            else:
                active_buttons = []

            # Last message from server = "START_GAME" - close connection with server responsible for handling lobby
            # Save 'last_msg[0].split("-")[1]' it is lobby_id - it will a token to created the same lobby with the same players
            if last_msg[0].split("-")[0] == "START_GAME":
                self.close_network_connection(connection, "THE GAME WILL START SOON")
                self.token = last_msg[0].split("-")[1]
                self.gameplay(run, cursor, df)
            # New lobby is created
            elif self.lobby_type == "START" and last_msg is not None:
                in_lobby = True
                self.lobby_type = "LOBBY_SHOW"

            # Print all available lobbies for a player - if he decides to join already created lobby
            elif self.lobby_type == "SHOW" and last_msg is not None:
                # If player wants to join a lobby which is full - present a message for 3 seconds that he cannot
                if cannot_join_lobby:
                    self.draw_pretty_text("CANNOT JOIN LOBBY", game_font, category_color,
                                          bg_color, pos, 8, 20, 28, last_rect)
                    pygame.display.update()
                    pygame.time.delay(3000)

                    join_button_dict, active_buttons, pos, in_lobby = self.present_available_lobbies(last_msg, active_buttons,
                                                                                           refresh_button_lobbies,
                                                                                           join_button_dict, pos)

                    cannot_join_lobby = False
                else:
                    join_button_dict, active_buttons, pos, in_lobby = self.present_available_lobbies(last_msg, active_buttons,
                                                                    refresh_button_lobbies, join_button_dict, pos)
            # Handle situation in which server sends a message that player cannot join a lobby
            elif last_msg[0] == "Cannot" and not cannot_join_lobby:
                cannot_join_lobby = True
                connection.send(f"SHOW\n")
                self.lobby_type = "SHOW"

            # Show the current state of a specific lobby
            elif self.lobby_type == "LOBBY_SHOW" and connection.get_latest_message() is not None:
                active_buttons.extend([exit_button, refresh_button_lobby, ready_button])
                last_msg = last_msg[0].split("-")
                last_rect = None
                last_rect = self.situation_in_lobby(last_msg, pos, last_rect)

            # Print all active buttons
            for button in active_buttons:
                if button is not None:
                    button.draw(screen)
                    button.change_color(mouse)

            pygame.display.flip()

    def show_round_results(self, run, last_msg, connection):
        exit_button = Button(
            width=SCREEN_WIDTH / 4,
            height=SCREEN_HEIGHT / 10,
            text="Exit Game",
            font=game_font,
            text_col=(100, 100, 100),
            x=SCREEN_WIDTH - SCREEN_WIDTH / 4 - 20,
            y=20
        )

        active_buttons = [exit_button]

        start_time = pygame.time.get_ticks()
        max_time = 15

        results = []

        try:
            if len(last_msg) < 3:
                raise ValueError("Invalid results message format")

            for result in last_msg[2:]:
                if result:
                    parts = result.split("_")
                    if len(parts) == 4:
                        results.append({
                            "nickname": parts[0],
                            "category": parts[1],
                            "answer": parts[2] if parts[2] else "None",
                            "points": parts[3].strip("-")
                        })
        except Exception as e:
            print(f"Error parsing results: {e}")
            results = []

        while run:
            screen.fill((235, 132, 250))
            mouse = pygame.mouse.get_pos()

            # Organize results by player
            player_results = defaultdict(list)
            for result in results:
                player_results[result["nickname"]].append(result)

            pos_y = 100
            last_rect = None
            for nickname, answers in player_results.items():
                total_points = sum(int(ans["points"]) for ans in answers)
                last_rect = self.draw_pretty_text(
                    f"{nickname} (Total: {total_points} points)",
                    game_font, category_color, bg_color, pos_y, prev_rect=last_rect
                )
                pos_y += 50
                last_rect.x += 200

                for ans in answers:
                    text = f"{ans['category']}: {ans['answer']} ({ans['points']} pts)"
                    last_rect = self.draw_pretty_text(
                        text, results_font, answer_color, bg_color, pos_y, prev_rect=last_rect
                    )
                    pos_y += 40

            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            time_left = max(0, max_time - elapsed_time)
            self.draw_text(
                f"Continuing in {time_left} seconds",
                results_font, category_color, SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT - 50
            )

            for button in active_buttons:
                button.draw(screen)
                button.change_color(mouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    connection.send(f"LEAVE {self.token}\n")
                    self.close_network_connection(connection, "LEAVING GAME")
                    self.menu(run, cursor, df)
                    return run
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_button.checkForClick(mouse):
                        connection.send(f"LEAVE {self.token}\n")
                        self.close_network_connection(connection, "LEAVING GAME")
                        self.menu(run, cursor, df)
                        return run
                if event.type == pygame.MOUSEMOTION:
                    for button in active_buttons:
                        button.change_color(mouse)

            if time_left == 0:
                return run

            pygame.display.flip()

        return run

    def show_leaderboard(self, run, last_msg, connection):
        exit_button = Button(
            width=SCREEN_WIDTH / 4,
            height=SCREEN_HEIGHT / 10,
            text="Exit to Menu",
            font=game_font,
            text_col=(100, 100, 100),
            x=SCREEN_WIDTH - SCREEN_WIDTH / 4 - 20,
            y=20
        )
        active_buttons = [exit_button]

        # Define players that are in the lobby
        players = []
        try:
            for player in last_msg[1:]:
                if player:
                    nickname, points = player.split("_")
                    players.append({"nickname": nickname, "points": int(points)})

        except Exception as e:
            print(f"Error parsing leaderboard: {e}")
            players = []

        while run:
            screen.fill((235, 132, 250))
            mouse = pygame.mouse.get_pos()
            last_rect = self.draw_pretty_text(
                "Final Leaderboard", game_font, category_color, bg_color, 50
            )
            pos_y = 100

            for player in players:
                last_rect = self.draw_pretty_text(
                    f"{player['nickname']}: {player['points']} points",
                    game_font, answer_color, bg_color, pos_y, prev_rect=last_rect
                )

                pos_y += 50

            for button in active_buttons:
                button.draw(screen)
                button.change_color(mouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_network_connection(connection, "LEAVING GAME")
                    self.menu(run, cursor, df)
                    return run
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_button.checkForClick(mouse):
                        self.close_network_connection(connection, "LEAVING GAME")
                        self.menu(run, cursor, df)
                        return run
                if event.type == pygame.MOUSEMOTION:
                    for button in active_buttons:
                        button.change_color(mouse)
            pygame.display.flip()
        return run

    def gameplay(self, run, cursor, df):
        """
        Runs the main gameplay loop

        Handles:
        Establishing game server connection
        Submitting and validating answers
        Countdown timer when a player submit his answer
        Displaying players’ scores and current round data
        Exiting the game if a player leaves
        """

        # Establish connection with server responsible for handling the game
        HOST = "localhost"
        PORT = 61112
        connection = EstablishConnection(HOST, PORT)

        # Send information to the server to which lobby player belongs and his nickname
        connection.send(f"CREATE_LOBBY {self.token} {self.nickname}\n")

        # Wait for presenting all players nicknames in a lobby
        time.sleep(2)

        # Last message from the server
        last_msg = connection.get_latest_message()

        # Send request to the server to show current punctation
        connection.send(f"SHOW_PUNCTUATION {self.token}\n")

        # Button for submitting the answer by the player
        accept_ans_button = None

        # Button for leaving a game - if there is two player in the game and one leaves the game ends
        exit_button = Button(
            width=SCREEN_WIDTH / 4,
            height=SCREEN_HEIGHT / 10,
            text="Exit Game",
            font=game_font,
            text_col=(100, 100, 100),
            x=SCREEN_WIDTH - SCREEN_WIDTH / 4 - 20,
            y=20
        )

        # List with active buttons
        active_buttons = [exit_button]

        # Flag for getting first letter in the first round
        initial_letter = True

        # Variables responsible for handling the counting during the game - if single player submit his answers - the counting begins
        start_timer = False
        confirmation_start_time = None
        time_left = None

        # If player submit empty answers three times - player is kicked from the game
        penalty_points = 0


        while run:
            mouse = pygame.mouse.get_pos()
            screen.fill((235, 132, 250))
            key = pygame.key.get_pressed()

            for event in pygame.event.get():
                # When players clicked on 'QUIT' button - player leaves a lobby, disconnects with the server and the main menu is visible
                if event.type == pygame.QUIT:
                    connection.send(f"LEAVE {self.token}\n")
                    self.close_network_connection(connection, "LEAVING GAME")
                    self.menu(run, cursor, df)
                if event.type == pygame.KEYDOWN:
                    # Logic responsible for inputting the answers and printing first letter in the particular round
                    if event.key == pygame.K_LEFT:
                        cursor -= 1
                    elif event.key == pygame.K_RIGHT:
                        cursor += 1
                    elif event.key == pygame.K_BACKSPACE:
                        if len(df.at[cursor, "Answer"]) > 1:
                            df.at[cursor, "Answer"] = df.at[cursor, "Answer"][:-1]
                    elif event.unicode.isalpha() or event.unicode.isspace():
                        df.at[cursor, "Answer"] += event.unicode
                    elif event.key == pygame.K_RETURN and accept_ans_button is not None:
                        penalty_points = self.handle_counting(penalty_points, connection)
                    else:
                        print("Wrong input!")
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # When players clicked on 'exit_button' button - player leaves a lobby, disconnects with the server and the main menu is visible
                    if exit_button.checkForClick(mouse):
                        connection.send(f"LEAVE {self.token}\n")
                        self.close_network_connection(connection, "LEAVING GAME")
                        self.menu(run, cursor, df)

                    # Player submit his answers as first, and we checked if he got any penalty points
                    if accept_ans_button is not None and accept_ans_button.checkForClick(mouse):
                        penalty_points = self.handle_counting(penalty_points, connection)


            # Logic responsible for time counting
            if not start_timer:
                confirmation_start_time = pygame.time.get_ticks()
            if start_timer:
                # When one player submit his answers - counting from 10 begins
                current_time = pygame.time.get_ticks()
                elapsed = current_time - confirmation_start_time
                time_left = max(0, 10 - elapsed // 1000)
                self.draw_text(f"Time left - {time_left}",  game_font, category_color,
                               SCREEN_WIDTH / 20 + SCREEN_WIDTH / 4 * 2.75 , 400)

            # When ten second leaves - we send answers for verification to server
            if time_left is not None and time_left == 0:
                time_left = None
                confirmation_start_time = pygame.time.get_ticks()
                start_timer = False
                answer = ''
                for ans, cat in zip(df['Answer'], df['Category']):
                    answer += ans + '_' + cat + '-'
                connection.send(f"GATHER_ANS {self.token} {answer}\n")

            # Print all active buttons
            for button in active_buttons:
                button.change_color(mouse)
                button.draw(screen)

            # Get latest message from the sever
            try:
                last_msg = str(connection.get_latest_message()).split("-")
            except Exception as e:
                last_msg = connection.get_latest_message()

            pos_y = SCREEN_HEIGHT / 6
            # Show points of all players in a lobby
            if last_msg is not None and last_msg[0] == 'SHOW_PUNCTUATION':
                pos_y, active_buttons, initial_letter, accept_ans_button = self.show_players_points(pos_y, last_msg,
                                                                                    initial_letter, active_buttons,
                                                                                                accept_ans_button)
            elif last_msg is not None and last_msg[0] == 'LEFT':
                connection.send(f"SHOW_PUNCTUATION {self.token}\n")
            # If server sends information = 'FINISH_LOBBY' - means that there is too little players to continue
            elif last_msg is not None and last_msg[0] == 'FINISH_LOBBY':
                self.close_network_connection(connection, "TOO LITTLE PLAYERS TO PLAY GAME")
                self.menu(run, cursor, df)
            # Start counting if one player submits his answers
            elif last_msg is not None and last_msg[0] == 'FINISH_GAME':
                self.show_leaderboard(run, last_msg, connection)
                return run
            elif last_msg is not None and last_msg[0] == 'START_COUNTING':
                start_timer = True
                connection.send(f"SHOW_PUNCTUATION {self.token}\n")
            # Check answers
            elif last_msg is not None and last_msg[0] == 'CHECK_ANSWERS':
                time.sleep(2)
                connection.send(f"CHECK_ANSWERS {self.token} {self.nickname}\n")
            # Show round results
            elif last_msg is not None and last_msg[0] == 'SHOW_RESULTS':
                df["Answer"] = [last_msg[1]] * len(game_categories)
                run = self.show_round_results(run, last_msg, connection)
                connection.send(f"SHOW_PUNCTUATION {self.token}\n")
            cursor = self.check_cursor(cursor)
            self.print_categories_and_answers()
            self.print_cursor(cursor, df)
            self.draw_text(f"Player: {self.nickname}", game_font, category_color, SCREEN_WIDTH / 5, 20)


            pygame.display.update()
            pygame.display.flip()

        return cursor



    def close_network_connection(self, connection, text):
        """
        Function closing connection with the server and,
        Displays message given in the declaration to the player
        """
        screen.fill((235, 132, 250))
        self.draw_pretty_text(text, game_font,
                       category_color, bg_color, 50)
        pygame.display.update()
        pygame.time.delay(3000)
        connection.client.shutdown(socket.SHUT_WR)
        time.sleep(1)
        connection.client.close()


    def handle_counting(self, penalty_points, connection):
        """
        Function is responsible for handling penalty point during a game
        If player submits two empty answers as first - got warning that next empty answers with submission result in kick
        If player submits three empty answers as first - is kicked from the game, disconnects from the server, main menu is presented
        If answers are okay - counting begins
        """
        check_lenght_of_ans = 0
        for word in df["Answer"]:
            if len(word) == 1:
                check_lenght_of_ans += 1
        if check_lenght_of_ans == NUMBER_OF_CATEGORIES:
            penalty_points += 1
        else:
            penalty_points = 0
        if penalty_points == 2:
            self.draw_text("ONE MORE EMPTY ANWER = YOU WILL GET KICK", game_font,
                           (255, 0, 0), SCREEN_WIDTH / 15, 250)
            pygame.display.update()
            pygame.time.delay(3000)
        if penalty_points == 3:
            self.draw_text("YOU SUMBIT THREE EMPTY ANSWERS ", game_font,
                           (255, 0, 0), SCREEN_WIDTH / 15, 150)
            self.draw_text("YOU WILL LEAVE A GAME", game_font,
                           (255, 0, 0), SCREEN_WIDTH / 15, 250)
            pygame.display.update()
            pygame.time.delay(3000)
            connection.send(f"LEAVE {self.token}\n")
            self.menu(run, cursor, df)
        else:
            connection.send(f"START_COUNTING {self.token}\n")
        return penalty_points



    def show_players_points(self, pos_y, last_msg, initial_letter, active_buttons, accept_ans_button):
        """
        Function prints all players in the game and their punctation
        """
        self.draw_text(f"PLAYERS", game_font, category_color,
                       SCREEN_WIDTH / 20 + SCREEN_WIDTH / 4 * 2.75, pos_y)
        pos_y += 50

        for msg in last_msg[2:]:
            msg = msg.split("_")
            self.draw_text(f"{msg[0]} - {msg[1]}", game_font, category_color,
                           SCREEN_WIDTH / 20 + SCREEN_WIDTH / 4 * 2.75, pos_y)
            pos_y += 30

        if initial_letter:
            accept_ans_button = Button(
                width=SCREEN_WIDTH / 4,
                height=SCREEN_HEIGHT / 10,
                text="Submit",
                font=game_font,
                text_col=(100, 100, 100),
                x=SCREEN_WIDTH - SCREEN_WIDTH / 4 - 20,
                y=pos_y + 70
            )
            df["Answer"] = [last_msg[1]] * len(game_categories)
            initial_letter = False
            active_buttons.append(accept_ans_button)
        return pos_y, active_buttons, initial_letter, accept_ans_button


class Button:
    def __init__(self, width, height, text, font, text_col, x, y):
        #self.x = SCREEN_WIDTH/2 - SCREEN_WIDTH/4
        #self.y = SCREEN_HEIGHT/2 - SCREEN_HEIGHT/10
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.text_col = text_col
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (200, 200, 200)
        self.hover_color = (255, 255, 255)
        self.current_color = self.color

    def set_text(self, text):
        self.text = text

    def get_text(self):
        return self.text

    def checkForClick(self, mouse):
        return self.rect.collidepoint(mouse)

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        text_surface = self.font.render(self.text, True, self.text_col)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def change_color(self, mouse):
        if self.rect.collidepoint(mouse):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color




if __name__ == "__main__":
    game = Game()