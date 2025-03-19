import pygame
import pandas as pd
import random
import string

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


def print_cursor(game_array):
    screen.blit(player_img, (game_array.iloc[cursor]["PosX"], game_array.iloc[cursor]["PosY"] + SCREEN_HEIGHT/4.5))


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


define_positions()

while run:
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
            elif event.unicode.isalpha():
                df.at[cursor, "Answer"] += event.unicode
            else:
                print("Wrong input!")

    #df = change_to_lowercase(df)
    cursor = check_cursor(cursor)

    screen.fill((235, 132, 250))


    print_categories_and_answers()
    print_cursor(df)


    pygame.display.update()
    pygame.display.flip()

pygame.quit()