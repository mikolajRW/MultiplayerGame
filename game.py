import pygame
import pandas as pd
import random
import string

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
player = pygame.Rect((30, 250, 40, 40))


game_font = pygame.font.Font(None, 32)
text_font = pygame.font.SysFont("Arial", 32)
user_text = ''

random_letter = random.choice(string.ascii_letters)

game_categories = ["Country", "City", "Animal", "Plant", "Pikers Song"]
game_answers = [random_letter.upper()] * len(game_categories)
df = pd.DataFrame({"Category": game_categories, "Answer": game_answers})
print(df)

cursor = 0
run = True


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


while run:

    key = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                cursor -= 1

                if check_cursor_two(cursor):
                    player.move_ip(-150, 0)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_RETURN:
                cursor += 1

                if check_cursor_two(cursor):
                    player.move_ip(150, 0)
            elif event.key == pygame.K_BACKSPACE:
                df.at[cursor, "Answer"] = df.at[cursor, "Answer"][:-1]
            elif event.key == pygame.K_1:
                print(df)
            else:
                df.at[cursor, "Answer"] += event.unicode
                user_text += event.unicode

    cursor = check_cursor(cursor)
    screen.fill((0, 0, 0))

    for i in range(len(df)):
        draw_text(df.iloc[i]["Category"], game_font, (255, 255, 255), 20 + 150 * i , 100)
        draw_text(df.iloc[i]["Answer"], game_font, (255, 255, 255), 20 + 150 * i, 200)

    pygame.draw.rect(screen, (255, 0, 0), player)
    text_surface = game_font.render(user_text, True, (255,255,255))
    screen.blit(text_surface, (0,0))
    pygame.display.update()
    pygame.display.flip()

print("change")
pygame.quit()