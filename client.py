import pygame
import random

pygame.init()
pygame.font.init()
# Constants
WINDOW_WIDTH = 746
WINDOW_HEIGHT = 645
SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255,0,0)

IMAGE = "board.png"
clock = pygame.time.Clock()
REFRESH_RATE = 60
FONT = pygame.font.Font(None, 36)

# 1- white, 2- blue, 0 -none
PLAYERS_SPOTS = {1: [2, 2], 2: [0, 0], 3: [0, 0], 4: [0, 0], 5: [0, 0], 6: [5, 1],
                 7: [0, 0], 8: [3, 1], 9: [0, 0], 10: [0, 0], 11: [0, 0], 12: [5, 2],
                 13: [5, 1], 14: [0, 0], 15: [0, 0], 16: [0, 0], 17: [3, 2], 18: [0, 0],
                 19: [5, 2], 20: [0, 0], 21: [0, 0], 22: [0, 0], 23: [0, 0], 24: [2, 1]}

SQUARES_POS = {1: [121.5, 525], 2: [164.5, 525], 3: [207.5, 525], 4: [250.5, 525], 5: [293.5, 525], 6: [336.5, 525],
               7: [405.5, 525], 8: [448.5, 525], 9: [491.5, 525], 10: [534.5, 525], 11: [579.5, 525], 12: [620.5, 525],
               13: [620.5, 120], 14: [579.5, 120], 15: [534.5, 120], 16: [491.5, 120], 17: [448.5, 120], 18: [405.5, 120],
               19: [336.5, 120], 20: [293.5, 120], 21: [250.5, 120], 22: [207.5, 120], 23: [164.5, 120], 24: [121.5, 120]}


def draw_board(board_dict, screen):
    for key in board_dict.keys():
        if type(board_dict[key]) == list and board_dict[key][0] > 0:
            if board_dict[key][1] == 1:
                color = WHITE
            elif board_dict[key][1] == 2:
                color = BLUE

            x, y = SQUARES_POS[key]
            for i in range(board_dict[key][0]):
                pygame.draw.circle(screen, color, [x, y], 20)
                if key <= 12:
                    y = y - 40
                else:
                    y = y + 40


def find_spot(x, y):
    x1 = 100
    x2 = 143
    value = 0
    for i in range(1, 13):
        if x1 <= x < x2:
            if 100 < y < 300:
                value = 25 - i
            elif 340 < y < 540:
                value = i
        x1 = x1 + 43
        x2 = x2 + 43
        if i == 6:
            x1 = x1 + 26
            x2 = x2 + 26
    return value


def turn(board, player):

    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Game")
    img = pygame.image.load(IMAGE)

    num = random.randint(1, 6)

    finish = False
    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True

            screen.blit(img, (0, 0))
            draw_board(board, screen)

            text = FONT.render("choose player to walk " + str(num) + " steps", True, RED)
            text_rect = text.get_rect()
            text_rect.center = (371, 50)
            screen.blit(text, text_rect)

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                spot1 = find_spot(x, y)
                if player == 1:#white
                    spot2 = spot1 + num
                elif player == 2:#blue
                    spot2 = spot1 - num
                if spot2 > 24:
                    # player out
                    PLAYERS_SPOTS[spot1][0] = PLAYERS_SPOTS[spot1][0] - 1
                else:
                    # regular turn
                    if board[spot2][0] == 0 or board[spot1][1] == board[spot2][1]:

                        board[spot1][0] = board[spot1][0] - 1
                        board[spot2][0] = board[spot2][0] + 1
                        board[spot2][1] = board[spot1][1]
                        print(board[spot1][1])
                        print(board[spot2][1])
                        if board[spot1][0] == 0:
                            board[spot1][1] = 0

                    else:
                        text = FONT.render("player can't go" , True, RED)
                        text_rect = text.get_rect()
                        text_rect.center = (371, 600)
                        screen.blit(text, text_rect)



            pygame.display.flip()
            clock.tick(REFRESH_RATE)










def main():

    response = turn(PLAYERS_SPOTS, 1)



if __name__ == "__main__":
    main()
    pygame.quit()