import socket
import pygame
import random
import pickle
import select

IP = '127.0.0.1'
PORT = 5555

pygame.init()
pygame.font.init()
# Constants
WINDOW_WIDTH = 746
WINDOW_HEIGHT = 645
SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)





WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

IMAGE = "board.png"
BOARD_IMG = pygame.image.load(IMAGE)
clock = pygame.time.Clock()
REFRESH_RATE = 60
FONT = pygame.font.Font(None, 36)

SQUARES_POS = {1: [121.5, 525], 2: [164.5, 525], 3: [207.5, 525], 4: [250.5, 525], 5: [293.5, 525], 6: [336.5, 525],
               7: [405.5, 525], 8: [448.5, 525], 9: [491.5, 525], 10: [534.5, 525], 11: [579.5, 525], 12: [620.5, 525],
               13: [620.5, 120], 14: [579.5, 120], 15: [534.5, 120], 16: [491.5, 120], 17: [448.5, 120], 18: [405.5, 120],
               19: [336.5, 120], 20: [293.5, 120], 21: [250.5, 120], 22: [207.5, 120], 23: [164.5, 120], 24: [121.5, 120]}

def cangetout(board, color):
    value = True
    for spot in board.keys():
        if color == 1:
            if spot > 6 and board[spot][0] > 0:
                value = False
        elif color ==2:
            if spot < 19 and board[spot][0] > 0:
                value = False
    return value
def draw_board(board_dict, player, screen):
    if player == "1":
        text = FONT.render("white", True, RED)
        text_rect = text.get_rect()
        text_rect.center = (30, 10)
        screen.blit(text, text_rect)
    elif player == "2":
        text = FONT.render("blue", True, RED)
        text_rect = text.get_rect()
        text_rect.center = (30, 10)
        screen.blit(text, text_rect)

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


def print_num(screen, num):
    # get a number and print it
    text = FONT.render("choose player to walk " + str(num) + " steps", True, RED)
    text_rect = text.get_rect()
    text_rect.center = (371, 50)
    screen.blit(text, text_rect)


def turn(screen, board, player, num, spot):
    turn_correct = False
    spot1 = spot
    if player == 1:# white
        spot2 = spot1 - num
    elif player == 2:#blue
        spot2 = spot1 + num
    if spot2 > 24 or spot2 < 1:
        # player out
        if (cangetout(board, player)):
            board[spot1][0] = board[spot1][0] - 1
            turn_correct =True

    else:
        # regular turn

        if board[spot2][0] == 0 or board[spot1][1] == board[spot2][1]:

            board[spot1][0] = board[spot1][0] - 1
            board[spot2][0] = board[spot2][0] + 1
            print("in original " + str(board[spot1][0]))
            print("in new " + str(board[spot2][0]))

            board[spot2][1] = board[spot1][1]

            if board[spot1][0] == 0:
                board[spot1][1] = 0
            turn_correct =True

        else:
            text = FONT.render("player can't go", True, RED)
            text_rect = text.get_rect()
            text_rect.center = (371, 600)
            screen.blit(text, text_rect)

    return board, turn_correct




def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))
    player = my_socket.recv(1024).decode()
    print("you are player number " + player)
    board = pickle.loads(my_socket.recv(1024))
    print(board)
    my_socket.send("good".encode())

    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Game")

    draw_board(board,player,  screen)

    got_board = False
    finish = False
    my_socket.settimeout(0.01)

    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True

            screen.blit(BOARD_IMG, (0, 0))

            if not got_board:
                rlist, wlist, xlist = select.select([my_socket], [], [], 0.01)
                if len(rlist)>0:
                    print("ready to receive")


                    response = my_socket.recv(1024)

                    board = pickle.loads(response)
                    print(board)
                    num = random.randint(1, 6)
                    got_board = True



            if got_board:
                print_num(screen, num)
                turn_correct = False
                if not turn_correct:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        spot = find_spot(x, y)

                        if board[spot][1] == int(player):
                            board2, turn_correct = turn(screen, board, int(player), num, spot)
                            screen.blit(BOARD_IMG, (0, 0))
                            draw_board(board2,player, screen)

                if turn_correct:
                    board_tosend = pickle.dumps(board2)
                    my_socket.send(board_tosend)
                    got_board = False

        draw_board(board, player, screen)
        pygame.display.flip()
        clock.tick(REFRESH_RATE)





if __name__ == "__main__":
    main()