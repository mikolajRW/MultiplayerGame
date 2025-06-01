import time
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

category_color = (255, 0, 0)
answer_color = (255, 255, 255)

game_font = pygame.font.Font(None, 50)
text_font = pygame.font.SysFont("Arial", 70)

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

class Establish_Connection:
    messages = []
    BUFFER = 1024
    def listen(self):
        while True:
            try:
                msg = self.client.recv(self.BUFFER).decode()
                self.messages.append(msg)
            except:
                break

    def __init__(self, HOST, PORT):
        # IP NASZEJ MASZYNY
        self.HOST = HOST
        self.PORT = PORT
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))
        threading.Thread(target=self.listen, daemon=True).start()
    def send(self, data):
        try:
            self.client.sendall(data.encode())
        except Exception as e:
            print(f"Error - {e}")

    def get_latest_message(self):
        return self.messages[-1] if self.messages else None

class Game:
    def __init__(self):
        self.define_positions()
        print(df)
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

    def check_cursor_two(self, cursor_f):
        if cursor_f < 0 or cursor_f > len(game_categories) - 1:
            return False
        else:
            return True

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    def change_to_lowercase(self,game_array):
        game_array["Answer"] = game_array["Answer"].str.lower()

        return game_array

    def check_answers(self, game_array):
        for _, position in game_array.iterrows():
            if position["Category"] == "Country":
                self.check_file("dictionaries/countries.txt", position["Answer"])
            elif position["Category"] == "City":
                self.check_file("dictionaries/cities.txt", position["Answer"])
            elif position["Category"] == "Animal":
                self.check_file("dictionaries/animals.txt", position["Answer"])
            elif position["Category"] == "Plant":
                self.check_file("dictionaries/plants.txt", position["Answer"])
            elif position["Category"] == "Thing":
                self.check_file("dictionaries/things.txt", position["Answer"])
            elif position["Category"] == "Occupation":
                self.check_file("dictionaries/occupations.txt", position["Answer"])
            elif position["Category"] == "Movie":
                self.check_file("dictionaries/movies.txt", position["Answer"])
            elif position["Category"] == "Sport":
                self.check_file("dictionaries/sports.txt", position["Answer"])

    def check_file(self, filepath, target_value):
        with open(filepath, 'r') as file:
            valid_answers = {line.strip().lower() for line in file}

        if target_value.lower() in valid_answers:
            print("10 points!")
        else:
            print("Wrong answer.")

    def menu(self, run, cursor, df):

        play_button = Button(width=SCREEN_WIDTH / 2, height=SCREEN_HEIGHT / 5, text="Play",
                             font=text_font, text_col=(100, 100, 100), x=SCREEN_WIDTH / 2 - SCREEN_WIDTH / 4,
                             y=SCREEN_HEIGHT - SCREEN_HEIGHT / 1.33)
        create_lobby_button = Button(width=SCREEN_WIDTH / 2, height=SCREEN_HEIGHT / 5, text="New Lobby",
                                     font=text_font, text_col=(100, 100, 100), x=SCREEN_WIDTH / 2 - SCREEN_WIDTH / 4,
                                     y=SCREEN_HEIGHT - SCREEN_HEIGHT / 2)
        join_lobby_button = Button(width=SCREEN_WIDTH / 2, height=SCREEN_HEIGHT / 5, text="Show Lobbies",
                                   font=text_font, text_col=(100, 100, 100), x=SCREEN_WIDTH / 2 - SCREEN_WIDTH / 4,
                                   y=SCREEN_HEIGHT - SCREEN_HEIGHT / 4)
        # exit_button = draw_text("EXIT", text_font, (255, 255, 255), SCREEN_WIDTH/2, SCREEN_HEIGHT/1.8)
        buttons = [join_lobby_button, create_lobby_button, play_button]

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
                    if play_button.checkForClick(mouse):
                        self.gameplay(run, cursor, df)
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
        """
        Handles player interaction with lobby join buttons.
        Iterates over join buttons (excluding the first) and sends a JOIN message to the server
        when a lobby button is clicked. Updates the lobby type to 'LOBBY_SHOW' upon joining.
        """
        # Iterate over buttons in join_button_dict - 'islice' method allows to iterate from the second object in dictionary
        for key, value in islice(join_button_dict.items(), 1, None):

            if value is not None and value.checkForClick(pygame.mouse.get_pos()):
                self.lobby_type = "LOBBY_SHOW"
                lobby_id = key.split('_')[2]
                # Send information to server that player with 'self.nickname' joined lobby with number 'lobby_id'
                connection.send(f"JOIN {lobby_id} {self.nickname}\n")
                break



    def handle_readiness_for_game(self, last_msg, connection):
        prev_error = 0
        if last_msg[0] == "NOT":
            prev_error = 1
        connection.send(f"READY {self.nickname} {last_msg[0 + prev_error]}\n")


    def create_lobby(self):
        HOST = "localhost"
        PORT = 61111
        connection = Establish_Connection(HOST, PORT)

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
                        self.handle_readiness_for_game(last_msg, connection)
                        ready_button.set_text("UNREADY")
                    # If players wants to change his readyness - click 'UNREADY' button
                    elif ready_button is not None and ready_button.checkForClick(pygame.mouse.get_pos()) and ready_button.get_text() == "UNREADY":
                        self.handle_readiness_for_game(last_msg, connection)
                        ready_button.set_text("READY")
                    if refresh_button_lobby is not None and refresh_button_lobby.checkForClick(pygame.mouse.get_pos()):
                        prev_error = 0
                        if last_msg[0] == "NOT":
                            prev_error = 1
                        print(f"LOBBY_SHOW {self.nickname} {last_msg[0 + prev_error]}\n")
                        connection.send(f"LOBBY_SHOW {last_msg[0 + prev_error]}\n")
                if event.type == pygame.MOUSEMOTION:
                    for button in active_buttons:
                        button.change_color(mouse)


            screen.fill((235, 132, 250))
            pos = 50

            last_msg = str(connection.get_latest_message()).split(" ")

            # Reset 'active_buttons' list in every iteration - to check changes
            active_buttons = []

            if in_lobby:
                active_buttons.extend([exit_button])
            else:
                active_buttons = []



            if last_msg[0].split("-")[0] == "START_GAME":
                self.close_network_connection(connection, "THE GAME WILL START SOON")
                self.token = last_msg[0].split("-")[1]
                self.gameplay(run, cursor, df)
            elif self.lobby_type == "START" and last_msg is not None:
                in_lobby = True
                self.lobby_type = "LOBBY_SHOW"

            elif self.lobby_type == "SHOW" and last_msg is not None:
                in_lobby = False

                active_buttons.append(refresh_button_lobbies)
                for msg in last_msg:
                    if msg == '\n' or msg is None:
                        continue
                    msg = msg.split("-")

                    self.draw_text(F"Lobby ID: {msg[0]}, amount of players: {len(msg)-1}/{MAX_LOBBY}",
                                        game_font, category_color, SCREEN_WIDTH / 10, pos)
                    var_name = f"join_button_{msg[0]}"
                    print("VARRR", var_name)
                    join_button_dict[var_name] = Button(width=SCREEN_WIDTH / 25, height=SCREEN_HEIGHT / 25, text="",
                                         font=text_font, text_col=(100, 100, 100),
                                         x=SCREEN_WIDTH / 10 + SCREEN_WIDTH / 1.25,
                                         y=pos)
                    print("BUUUUUT", join_button_dict)
                    active_buttons.extend([join_button_dict[var_name]])

                    pos += 50

            elif self.lobby_type == "LOBBY_SHOW" and connection.get_latest_message() is not None:
                # ogarnac który indeks, jesy wybierany ale to petla po przyciskach

                active_buttons.extend([exit_button, refresh_button_lobby, ready_button])
                # play_button = Button(width=SCREEN_WIDTH / 2, height=SCREEN_HEIGHT / 5, text="Start Play",
                #                      font=text_font, text_col=(100, 100, 100),
                #                      x=SCREEN_WIDTH / 2 - SCREEN_WIDTH / 4,
                #                      y=SCREEN_HEIGHT - SCREEN_HEIGHT / 2)
                last_msg = last_msg[0].split("-")

                if last_msg[0] == "NOT":
                    self.draw_text(F"Lobby ID: {last_msg[1]}, amount of players: {last_msg[2]}/{MAX_LOBBY}",
                                   game_font, category_color, SCREEN_WIDTH / 10, pos)
                    self.draw_text("Not enough players to start a game", game_font, category_color,
                                           SCREEN_WIDTH / 10, pos + 50)
                    readyness_type = "READY"
                   # connection.send(f"LOBBY_SHOW {last_msg[1]}\n")
                else:
                    self.draw_text(F"Lobby ID: {last_msg[0]}, amount of players: {last_msg[1]}/{MAX_LOBBY}",
                                        game_font, category_color, SCREEN_WIDTH / 10, pos)
                    self.draw_text(f"{last_msg[-1][0]}/{last_msg[1]} READY", game_font, category_color,
                                           SCREEN_WIDTH / 10, pos + 50)
                   # connection.send(f"LOBBY_SHOW {last_msg[0]}\n")

                if last_msg[-1][0].isdigit() and last_msg[1].isdigit():
                    game_start = int(last_msg[-1][0]) - int(last_msg[1])
                else:
                    game_start = -1

            for button in active_buttons:
                if button is not None:
                    button.draw(screen)
                    button.change_color(mouse)

            pygame.display.flip()


    def gameplay(self, run, cursor, df):
        HOST = "localhost"
        PORT = 61112
        letter_for_round = None
        connection = Establish_Connection(HOST, PORT)
        print(self.token)
        connection.send(f"CREATE_LOBBY {self.token} {self.nickname}\n")
        last_msg = connection.get_latest_message()
        print(last_msg)
        time.sleep(1)
        connection.send(f"SHOW_PUNCTUATION {self.token}\n")
        accept_ans_button = None
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
        initial_letter = True
        start_timer = False
        confirmation_start_time = None
        time_left = None
        penalty_points = 0
        while run:
            mouse = pygame.mouse.get_pos()
            screen.fill((235, 132, 250))
            key = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # dodaj wychodzenie z lobby
                    self.menu(run, cursor, df)
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            cursor -= 1
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_RETURN:
                            cursor += 1
                        elif event.key == pygame.K_BACKSPACE:
                            if len(df.at[cursor, "Answer"]) > 1:
                                df.at[cursor, "Answer"] = df.at[cursor, "Answer"][:-1]
                        elif event.key == pygame.K_1:
                            print(df)
                        elif event.key == pygame.K_2:
                            self.check_answers(df)
                        elif event.unicode.isalpha() or event.unicode.isspace():
                            df.at[cursor, "Answer"] += event.unicode
                        else:
                            print("Wrong input!")
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_button.checkForClick(mouse):
                        connection.send(f"LEAVE {self.token}\n")
                        self.close_network_connection(connection, "IDIOT YOU LEAVE GAME - FUCK YOU")
                        self.menu(run, cursor, df)
                    if accept_ans_button is not None and accept_ans_button.checkForClick(mouse):
                        penalty_points = self.handle_counting(penalty_points, connection)
                        print(penalty_points)

            if not start_timer:
                confirmation_start_time = pygame.time.get_ticks()
            if start_timer:
                current_time = pygame.time.get_ticks()
                elapsed = current_time - confirmation_start_time
                time_left = max(0, 10 - elapsed // 1000)
                self.draw_text(f"Time left - {time_left}", game_font, (255, 0, 0),
                               SCREEN_WIDTH / 20 + SCREEN_WIDTH / 4 * 2.75 , 400)
            if time_left is not None and time_left == 0:
                time_left = None
                confirmation_start_time = pygame.time.get_ticks()
                start_timer = False
                answer = ''
                for ans, cat in zip(df['Answer'], df['Category']):
                    answer += ans + '_' + cat + '-'
                connection.send(f"GATHER_ANS {self.token} {answer}\n")


            for button in active_buttons:
                button.change_color(mouse)
                button.draw(screen)
            try:
                last_msg = str(connection.get_latest_message()).split("-")
            except Exception as e:
                last_msg = connection.get_latest_message()


            pos_y = SCREEN_HEIGHT / 6
            if last_msg is not None and last_msg[0] == 'SHOW_PUNCTUATION':
                self.draw_text(f"PLAYERS", game_font, category_color,
                               SCREEN_WIDTH / 20 + SCREEN_WIDTH / 4 * 2.75, pos_y)
                pos_y += 50

                for msg in last_msg[2:]:
                    msg = msg.split("_")
                    print(msg)
                    self.draw_text(f"{msg[0]} - {msg[1]}", game_font, category_color,
                                   SCREEN_WIDTH / 20 + SCREEN_WIDTH / 4 * 2.75,  pos_y)
                    pos_y += 30

                if initial_letter:
                    accept_ans_button = Button(
                        width=SCREEN_WIDTH / 4,
                        height=SCREEN_HEIGHT / 10,
                        text="Submit",
                        font=game_font,
                        text_col=(100, 100, 100),
                        x=SCREEN_WIDTH - SCREEN_WIDTH / 4 - 20,
                        y=pos_y+70
                    )
                    df["Answer"] = [last_msg[1]] * len(game_categories)
                    initial_letter = False
                    active_buttons.append(accept_ans_button)
            elif last_msg is not None and last_msg[0] == 'LEFT':
                connection.send(f"SHOW_PUNCTUATION {self.token}\n")
            elif last_msg is not None and last_msg[0] == 'FINISH_LOBBY':
                self.close_network_connection(connection, "SOME IDIOT LEAVE GAME - TOO LITTLE PLAYERS TO PLAY GAME")
                self.menu(run, cursor, df)
            elif last_msg is not None and last_msg[0] == 'START_COUNTING':
                start_timer = True
                connection.send(f"SHOW_PUNCTUATION {self.token}\n")
            elif last_msg is not None and last_msg[0] == 'CHECK_ANSWERS':
                connection.send(f"CHECK_ANSWERS {self.token}\n")
            elif last_msg is not None and last_msg[0] == 'SHOW_RESULTS':
                df["Answer"] = [last_msg[1]] * len(game_categories)
                connection.send(f"SHOW_PUNCTUATION {self.token}\n")
            cursor = self.check_cursor(cursor)
            self.print_categories_and_answers()
            self.print_cursor(cursor, df)



            pygame.display.update()
            pygame.display.flip()

        return cursor

    def close_network_connection(self, connection, text):
        screen.fill((235, 132, 250))
        self.draw_text(text, game_font,
                       category_color, SCREEN_WIDTH / 10, 50)
        pygame.display.update()
        pygame.time.delay(3000)
        connection.client.shutdown(socket.SHUT_WR)
        time.sleep(1)
        connection.client.close()


    def handle_counting(self, penalty_points, connection):
        check_lenght_of_ans = 0
        for word in df["Answer"]:
            if len(word) == 1:
                check_lenght_of_ans += 1
        print(check_lenght_of_ans)
        if check_lenght_of_ans == NUMBER_OF_CATEGORIES:
            penalty_points += 1
        else:
            penalty_points = 0
        print(penalty_points)
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
'''
    def confirm_finishing_round(self):
        confirmation_start_time = pygame.time.get_ticks()
        confirmation_timeout = 5000
        confirmed = False
        waiting_for_confirmation = True
        while waiting_for_confirmation:
            mouse = pygame.mouse.get_pos()
            current_time = pygame.time.get_ticks()
            elapsed = current_time - confirmation_start_time
            screen.fill((235, 132, 250))
            self.draw_text("ARE YOU SURE OF YOUR ANSWERS", game_font,
                           category_color, SCREEN_WIDTH / 10, 50)

            time_left = max(0, 5 - elapsed // 1000)
            self.draw_text(f"Time left - {time_left}", game_font, (255, 0, 0), SCREEN_WIDTH / 10, 150)

            confirm_button = Button(width=SCREEN_WIDTH / 2, height=SCREEN_HEIGHT / 5, text="YES",
                                    font=text_font, text_col=(100, 100, 100),
                                    x=SCREEN_WIDTH / 2 - SCREEN_WIDTH / 4,
                                    y=350)

            confirm_button.change_color(mouse)
            confirm_button.draw(screen)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if confirm_button.checkForClick(mouse):
                        confirmed = True
                        waiting_for_confirmation = False

            if elapsed > confirmation_timeout:
                waiting_for_confirmation = False

        return confirmed
    '''
'''
pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
player = pygame.Rect((30, 250, 40, 40))
player_img = pygame.image.load("images/cursor.png")
player_img = pygame.transform.scale(player_img, (40, 40))
#player.x = 150

player_rect = player_img.get_rect(topleft=(30, 250))

category_color = (255, 0, 0)
answer_color = (255, 255, 255)

game_font = pygame.font.Font(None, 50)
text_font = pygame.font.SysFont("Arial", 70)

random_letter = random.choice(string.ascii_letters)

letters = [char for char in string.ascii_uppercase if char not in {'Q', 'X'}]

game_categories = ["Country", "City", "Animal", "Plant", "Thing", "Occupation", "Movie", "Sport"]
game_answers = [random.choice(letters)] * len(game_categories)
positions_x = [1.0] * len(game_categories)
positions_y = [1.0] * len(game_categories)
df = pd.DataFrame({"Category": game_categories, "Answer": game_answers, "PosX:": positions_x, "PosY": positions_y})
print(df)

cursor = 0
run = True
'''

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
            #print(f"Mouse at {mouse} over {self.rect}? {self.rect.collidepoint(mouse)}")
        else:
            self.current_color = self.color
            #print(f"Mouse at {mouse} over {self.rect}? {self.rect.collidepoint(mouse)}")


'''
def define_positions():
    for index in range(len(df)):
        if index < 4:
            df.at[index, "PosX"] = SCREEN_WIDTH/20 + SCREEN_WIDTH/4 * index
            df.at[index, "PosY"] = SCREEN_HEIGHT/6
        else:
            df.at[index, "PosX"] = SCREEN_WIDTH / 20 + SCREEN_WIDTH / 4 * (index-4)
            df.at[index, "PosY"] = SCREEN_HEIGHT/1.7


def print_categories_and_answers():
    for i in range(len(df)):
        draw_text(df.iloc[i]["Category"], game_font, category_color, df.iloc[i]["PosX"] , df.iloc[i]["PosY"])
        draw_text(df.iloc[i]["Answer"], game_font, answer_color, df.iloc[i]["PosX"], df.iloc[i]["PosY"] + SCREEN_HEIGHT/8)


def print_cursor(cursor_temp, game_array):
    screen.blit(player_img, (game_array.iloc[cursor_temp]["PosX"], game_array.iloc[cursor_temp]["PosY"] + SCREEN_HEIGHT/4.5))


def check_cursor(cursor_f):
    if cursor_f < 0:
        cursor_f = 0
    elif cursor_f > len(game_categories) - 1:
        cursor_f -= 1

    return cursor_f


def check_cursor_two(cursor_f):
    if cursor_f < 0 or cursor_f > len(game_categories) - 1:
        return False
    else:
        return True


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def change_to_lowercase(game_array):
    game_array["Answer"] = game_array["Answer"].str.lower()

    return game_array


def check_answers(game_array):
    for _, position in game_array.iterrows():
        if position["Category"] == "Country":
            check_file("dictionaries/countries.txt", position["Answer"])
        elif position["Category"] == "City":
            check_file("dictionaries/cities.txt", position["Answer"])
        elif position["Category"] == "Animal":
            check_file("dictionaries/animals.txt", position["Answer"])
        elif position["Category"] == "Plant":
            check_file("dictionaries/plants.txt", position["Answer"])
        elif position["Category"] == "Thing":
            check_file("dictionaries/things.txt", position["Answer"])
        elif position["Category"] == "Occupation":
            check_file("dictionaries/occupations.txt", position["Answer"])
        elif position["Category"] == "Movie":
            check_file("dictionaries/movies.txt", position["Answer"])
        elif position["Category"] == "Sport":
            check_file("dictionaries/sports.txt", position["Answer"])


def check_file(filepath, target_value):
    with open(filepath, 'r') as file:
        valid_answers = {line.strip().lower() for line in file}

    if target_value.lower() in valid_answers:
        print("10 points!")
    else:
        print("Wrong answer.")



define_positions()

def menu(run, cursor, df):
    while run:
        screen.fill((235, 132, 250))
        menu_text = text_font.render("Menu", True, (0,0,0))
        text_react = menu_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/10))
        screen.blit(menu_text, text_react)
        play_button = Button(width=SCREEN_WIDTH / 2, height=SCREEN_HEIGHT / 5, text ="Play",
                             font = text_font, text_col = (100,100,100))
        #exit_button = draw_text("EXIT", text_font, (255, 255, 255), SCREEN_WIDTH/2, SCREEN_HEIGHT/1.8)
        buttons = [play_button]
        for button in buttons:
            button.draw(screen)

        key = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForClick(mouse=pygame.mouse.get_pos()):
                    gameplay(run, cursor, df)
            if event.type == pygame.MOUSEMOTION:
                for button in buttons:
                    button.change_color(mouse=pygame.mouse.get_pos())

        cursor = check_cursor(cursor)
        pygame.display.update()
        pygame.display.flip()


def gameplay(run, cursor, df):
    while run:
        screen.fill((235, 132, 250))
        key = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    cursor -= 1

                elif event.key == pygame.K_RIGHT or event.key == pygame.K_RETURN:
                    cursor += 1

                elif event.key == pygame.K_BACKSPACE:

                    if len(df.at[cursor, "Answer"]) > 1:
                        df.at[cursor, "Answer"] = df.at[cursor, "Answer"][:-1]
                elif event.key == pygame.K_1:
                    print(df)
                elif event.key == pygame.K_2:
                    check_answers(df)
                elif event.unicode.isalpha() or event.unicode.isspace():
                    df.at[cursor, "Answer"] += event.unicode
                else:
                    print("Wrong input!")

        #df = change_to_lowercase(df)
        cursor = check_cursor(cursor)




        print_categories_and_answers()
        print_cursor(cursor, df)


        pygame.display.update()
        pygame.display.flip()

    return cursor


menu(run, cursor, df)
pygame.quit()'''

if __name__ == "__main__":
    game = Game()