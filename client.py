import socket
import pygame
import random
import select
import protocol
import time
import logging
import os

pygame.init()
pygame.font.init()

# Constants
IP = '127.0.0.1'
PORT = 5555

WINDOW_WIDTH = 746
WINDOW_HEIGHT = 645
SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

LOG_FORMAT = '%(levelname)s | %(asctime)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/client.log'

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

DURATION = 30

IMAGE = "board.png"
BOARD_IMG = pygame.image.load(IMAGE)
clock = pygame.time.Clock()
REFRESH_RATE = 60
FONT = pygame.font.Font(None, 36)

SQUARES_POS = {1: [121.5, 525], 2: [164.5, 525], 3: [207.5, 525], 4: [250.5, 525], 5: [293.5, 525], 6: [336.5, 525],
               7: [405.5, 525], 8: [448.5, 525], 9: [491.5, 525], 10: [534.5, 525], 11: [579.5, 525], 12: [620.5, 525],
               13: [620.5, 120], 14: [579.5, 120], 15: [534.5, 120], 16: [491.5, 120], 17: [448.5, 120], 18: [405.5, 120],
               19: [336.5, 120], 20: [293.5, 120], 21: [250.5, 120], 22: [207.5, 120], 23: [164.5, 120], 24: [121.5, 120],
               -100: [65, 525], 100: [65, 120]}


def draw_board(board, color, screen):
    """
    the function received a dictionary and the color of the player and draws the board on the screen
    :param board: dictionary of the board
    :param color: the color of the player in str
    :param screen: the screen
    :return: none
    """
    if color == "1":
        text = FONT.render("white", True, RED)
        text_rect = text.get_rect()
        text_rect.center = (50, 20)
        screen.blit(text, text_rect)
    elif color == "2":
        text = FONT.render("blue", True, RED)
        text_rect = text.get_rect()
        text_rect.center = (50, 10)
        screen.blit(text, text_rect)

    for key in board.keys():
        if board[key][1] == "1":
            col = WHITE
        elif board[key][1] == "2":
            col = BLUE
        else:
            col = RED

        if col == WHITE or col == BLUE:
            x, y = SQUARES_POS[key]
            for i in range(board[key][0]):
                pygame.draw.circle(screen, col, [x, y], 20)
                if key <= 12:
                    y = y - 40
                else:
                    y = y + 40


def find_spot(x, y):
    """
    checks in which spot on board the client has pressed
    :param x: x pos
    :param y: y pos
    :return: the spot on the board of x and y, if there is an error return -1
    """
    value = 0
    try:
        x1 = 100
        x2 = 143
        for i in range(1, 13):
            if x1 <= x < x2:
                if 100 < y < 330:
                    value = 25 - i
                elif 310 < y < 540:
                    value = i
            x1 = x1 + 43
            x2 = x2 + 43
            if i == 6:
                x1 = x1 + 26
                x2 = x2 + 26
        if 57 < x < 100:
            if 100 < y < 300:
                value = 100
            elif 340 < y < 540:
                value = -100
    except Exception as e:
        logging.debug(f"An error occurred: {e}")
        value = -1
    finally:
        return value


def turn(screen, board, color, num, spot1):
    """
    gets the data for this turn and moves the piece according to num(cube) and the spot
    :param screen: the screen
    :param board: dictionary of the board
    :param color: color of the player
    :param num: the num of the cube for this turn
    :param spot1: the spot the client pressed on
    :return: the board after the turn and true if the turn is correct or false if not
    """
    turn_correct = False
    try:

        if color == "1":
            spot2 = spot1 - num
        elif color == "2":
            spot2 = spot1 + num
        else:
            spot2 = 0

        if 1 <= spot1 <= 24:
            if spot2 > 24 or spot2 < 1:
                # player out
                logging.debug(can_get_out(board, color))
                if can_get_out(board, color):
                    logging.debug("player go out")
                    board[spot1][0] = board[spot1][0] - 1
                    turn_correct = True

            else:
                # regular turn

                if board[spot2][0] == 0 or board[spot1][1] == board[spot2][1]:

                    board[spot1][0] = board[spot1][0] - 1
                    board[spot2][0] = board[spot2][0] + 1

                    board[spot2][1] = board[spot1][1]

                    if board[spot1][0] == 0:
                        board[spot1][1] = "0"
                    turn_correct = True

                elif board[spot2][0] == 1 and board[spot1][1] != board[spot2][1]:
                    logging.debug("eat other player")
                    if board[spot2][1] == "1":
                        board[100][0] = board[100][0] + 1
                    elif board[spot2][1] == "2":
                        board[-100][0] = board[-100][0] + 1

                    board[spot1][0] = board[spot1][0] - 1
                    board[spot2][1] = board[spot1][1]

                    if board[spot1][0] == 0:
                        board[spot1][1] = "0"

                    turn_correct = True

                else:
                    text = FONT.render("player can't go", True, RED)
                    text_rect = text.get_rect()
                    text_rect.center = (371, 600)
                    screen.blit(text, text_rect)

    except socket.error as err:
        logging.debug('received socket error ' + str(err))
        turn_correct = False
    finally:
        return board, turn_correct


def turn_eaten_player(screen, board, color, num, spot1):
    """
    special turn if one of the pieces was "eaten" and needs to go back to the board
    :param screen: the screen
    :param board: dictionary of the board
    :param color: color of the player
    :param num: the num of the cube for this turn
    :param spot1: the spot the client pressed on
    :return: the board after the turn and true if the turn is correct or false if not
    """
    turn_correct = False
    try:
        if color == "1":
            spot2 = 25 - num
        elif color == "2":
            spot2 = num
        else:
            spot2 = 0

        if 1 <= spot2 <= 24:
            if board[spot2][0] == 0 or board[spot1][1] == board[spot2][1]:
                board[spot1][0] = board[spot1][0] - 1
                board[spot2][0] = board[spot2][0] + 1
                board[spot2][1] = board[spot1][1]
                turn_correct = True

            elif board[spot2][0] == 1 and board[spot1][1] != board[spot2][1]:
                logging.debug("eat other player")
                if board[spot2][1] == "1":
                    board[100][0] = board[100][0] + 1
                elif board[spot2][1] == "2":
                    board[-100][0] = board[-100][0] + 1

                board[spot1][0] = board[spot1][0] - 1
                board[spot2][1] = board[spot1][1]
                turn_correct = True

            else:
                text = FONT.render("player can't go", True, RED)
                text_rect = text.get_rect()
                text_rect.center = (371, 600)
                screen.blit(text, text_rect)

    except socket.error as err:
        logging.debug('received socket error ' + str(err))
        turn_correct = False
    finally:
        return board, turn_correct


def can_get_out(board, color):
    """
    check if the player can remove his pieces out
    :param board: dictionary of the board
    :param color: color of the player
    :return: true if player can get out and false if not
    """
    value = True
    if color == "1":
        for s in board.keys():
            if s > 6:
                if board[s][0] > 0 and board[s][1] == "1":
                    if s != 100:
                        value = False

    elif color == "2":
        for s in board.keys():
            if s < 19 and board[s][0] > 0:
                if board[s][0] > 0 and board[s][1] == "2":
                    if s != -100:
                        value = False
    return value


def print_num(screen, num):
    """
    print the num for this turn on the screen
    """
    text = FONT.render("choose player to walk " + str(num) + " steps", True, RED)
    text_rect = text.get_rect()
    text_rect.center = (371, 50)
    screen.blit(text, text_rect)


def end_screen(color, board, screen):
    """
    draws the end screen after the game over
    :param color: color of the player who won
    :param board: dict of the board
    :param screen: the screen
    :return: none
    """
    try:
        finish = False
        if color == "1":
            msg = "white has won"
        elif color == "2":
            msg = "blue has won"
        elif color == "0":
            msg = "the other player disconnect, you have won"
        else:
            msg = "the server fall, game over"

        while not finish:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = True

                draw_board(board, color, screen)
                text = FONT.render(msg, True, BLUE)
                text_rect = text.get_rect()
                text_rect.center = (371, 320)
                screen.blit(text, text_rect)

                pygame.display.flip()
                clock.tick(REFRESH_RATE)

    except socket.error as err:
        logging.debug('received socket error ' + str(err))
    finally:
        return


def waiting_screen(screen, my_socket):
    """
    drawing a waiting screen until receiving the first msg from server
    :param screen: the screen
    :param my_socket: socket of client
    :return: func and board - the msg from server to start the game
    """
    try:
        finish = False
        while not finish:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = True

            rlist, wlist, xlist = select.select([my_socket], [], [], 0.01)
            if len(rlist) > 0:
                func, board1 = protocol.receive_protocol(my_socket)
                return func, board1

            else:
                text = FONT.render("waiting for another player", True, BLUE)
                text_rect = text.get_rect()
                text_rect.center = (371, 320)
                screen.blit(text, text_rect)

                pygame.display.flip()
                clock.tick(REFRESH_RATE)
    except socket.error as err:
        logging.debug('received socket error ' + str(err))
        return "-1", "-1"


def main():
    """
    the main function of the client. the client connects to the server and waits to start the game
    in each turn the client receives the board from the server, he gets a num and presses on the board to move
    a piece and do his turn. In the end of the turn he will send the board back to the server after the changes
     and wait to the next turn.
    :return: none
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((IP, PORT))
        screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Game")

        func, board = waiting_screen(screen, my_socket)
        my_socket.send(protocol.send_protocol(func, board))
        color = "0"
        if func == "11":
            color = "1"
        elif func == "12":
            color = "2"

        logging.debug("color: " + color)

        got_board = False
        finish = False
        if color != "0":
            while not finish:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        finish = True

                screen.blit(BOARD_IMG, (0, 0))

                if not got_board:
                    rlist, wlist, xlist = select.select([my_socket], [], [], 0.01)
                    if len(rlist) > 0:
                        func, board2 = protocol.receive_protocol(my_socket)
                        logging.debug("received: " + func)
                        if func == "20":
                            board = board2
                            got_board = True
                            start_time = time.time()
                            time_left = DURATION
                            num = random.randint(1, 6)
                            logging.debug("num for this turn: " + str(num))

                        elif func == "30" or func == "31" or func == "32":
                            logging.debug("GAME OVER")
                            my_socket.send(protocol.send_protocol(func, board2))
                            logging.debug(protocol.send_protocol(func, board2))
                            color = func[1]
                            end_screen(color, board2, screen)
                            break

                if got_board:
                    print_num(screen, num)
                    turn_correct = False
                    if not turn_correct:
                        if time_left > 0:
                            elapsed_time = time.time() - start_time
                            time_left = max(DURATION - int(elapsed_time), 0)
                            pygame.time.delay(100)
                            text = FONT.render("Time Left: " + str(time_left), True, RED)
                            text_rect = text.get_rect()
                            text_rect.center = (650, 15)
                            screen.blit(text, text_rect)

                            for event in pygame.event.get():
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    x, y = pygame.mouse.get_pos()
                                    spot = find_spot(x, y)
                                    logging.debug("press on spot: " + str(spot))
                                    if (color == "1" and board[100][0] > 0) or (color == "2" and board[-100][0] > 0):
                                        if (color == "1" and spot == 100) or (color == "2" and spot == -100):
                                            logging.debug("back to game")
                                            board, turn_correct = turn_eaten_player(screen, board, color, num, spot)

                                    else:
                                        if 0 < spot < 25:
                                            if board[spot][1] == color:
                                                logging.debug("regular turn")
                                                board, turn_correct = turn(screen, board, color, num, spot)

                                                screen.blit(BOARD_IMG, (0, 0))
                                                draw_board(board, color, screen)
                                    logging.debug(turn_correct)
                        else:
                            turn_correct = True

                        if turn_correct:
                            my_socket.send(protocol.send_protocol("20", board))
                            logging.debug("send: 20")
                            got_board = False

                draw_board(board, color, screen)
                pygame.display.flip()
                clock.tick(REFRESH_RATE)

    except socket.error as err:
        logging.debug('received socket error ' + str(err))
    except Exception as e:
        logging.debug(f"An error occurred: {e}")

    finally:
        my_socket.close()
        logging.debug("close screen")


if __name__ == "__main__":
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    board_a = {1: [2, "2"], 2: [0, "0"], 3: [0, "0"], 4: [0, "0"], 5: [0, "0"], 6: [5, "1"],
               7: [0, "0"], 8: [3, "1"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [5, "2"],
               13: [5, "1"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [3, "2"], 18: [0, "0"],
               19: [5, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [0, "0"], 24: [2, "1"]}
    assert not can_get_out(board_a, "1")
    assert not can_get_out(board_a, "2")

    board_a = {1: [2, "2"], 2: [0, "0"], 3: [0, "0"], 4: [5, "1"], 5: [5, "1"], 6: [5, "1"],
               7: [0, "0"], 8: [0, "0"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [5, "2"],
               13: [0, "0"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [3, "2"], 18: [0, "0"],
               19: [5, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [0, "0"], 24: [0, "0"]}
    assert can_get_out(board_a, "1")

    assert find_spot(120, 110) == 24
    assert find_spot(120, 400) == 1
    assert find_spot(300, 400) == 5

    screen_a = pygame.display.set_mode(SIZE)
    board_a = {1: [2, "2"], 2: [0, "0"], 3: [0, "0"], 4: [0, "0"], 5: [0, "0"], 6: [5, "1"],
               7: [0, "0"], 8: [3, "1"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [5, "2"],
               13: [5, "1"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [3, "2"], 18: [0, "0"],
               19: [5, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [0, "0"], 24: [2, "1"]}
    color_a = "2"
    num_a = 1
    spot_a = 1
    assert turn(screen_a, board_a, color_a, num_a, spot_a) == (board_a, True)

    board_a = {1: [2, "2"], 2: [0, "0"], 3: [0, "0"], 4: [0, "0"], 5: [0, "0"], 6: [5, "1"],
               7: [0, "0"], 8: [3, "1"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [5, "2"],
               13: [5, "1"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [3, "2"], 18: [0, "0"],
               19: [5, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [0, "0"], 24: [2, "1"]}
    color_a = "2"
    num_a = 5
    spot_a = 1
    assert turn(screen_a, board_a, color_a, num_a, spot_a) == (board_a, False)

    board_a = {1: [2, "2"], 2: [0, "0"], 3: [0, "0"], 4: [0, "0"], 5: [0, "0"], 6: [5, "1"],
               7: [0, "0"], 8: [3, "1"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [5, "2"],
               13: [5, "1"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [3, "2"], 18: [0, "0"],
               19: [5, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [0, "0"], 24: [2, "1"]}

    assert protocol.send_protocol("11", board_a) == b'11262!\x80\x04\x95\xfb\x00\x00\x00\x00\x00\x00\x00}\x94(K\x01]\x94(K\x02\x8c\x012\x94eK\x02]\x94(K\x00\x8c\x010\x94eK\x03]\x94(K\x00h\x04eK\x04]\x94(K\x00h\x04eK\x05]\x94(K\x00h\x04eK\x06]\x94(K\x05\x8c\x011\x94eK\x07]\x94(K\x00h\x04eK\x08]\x94(K\x03h\teK\t]\x94(K\x00h\x04eK\n]\x94(K\x00h\x04eK\x0b]\x94(K\x00h\x04eK\x0c]\x94(K\x05h\x02eK\r]\x94(K\x05h\teK\x0e]\x94(K\x00h\x04eK\x0f]\x94(K\x00h\x04eK\x10]\x94(K\x00h\x04eK\x11]\x94(K\x03h\x02eK\x12]\x94(K\x00h\x04eK\x13]\x94(K\x05h\x02eK\x14]\x94(K\x00h\x04eK\x15]\x94(K\x00h\x04eK\x16]\x94(K\x00h\x04eK\x17]\x94(K\x00h\x04eK\x18]\x94(K\x02h\teu.'
    assert protocol.send_protocol("20", board_a) == b'20262!\x80\x04\x95\xfb\x00\x00\x00\x00\x00\x00\x00}\x94(K\x01]\x94(K\x02\x8c\x012\x94eK\x02]\x94(K\x00\x8c\x010\x94eK\x03]\x94(K\x00h\x04eK\x04]\x94(K\x00h\x04eK\x05]\x94(K\x00h\x04eK\x06]\x94(K\x05\x8c\x011\x94eK\x07]\x94(K\x00h\x04eK\x08]\x94(K\x03h\teK\t]\x94(K\x00h\x04eK\n]\x94(K\x00h\x04eK\x0b]\x94(K\x00h\x04eK\x0c]\x94(K\x05h\x02eK\r]\x94(K\x05h\teK\x0e]\x94(K\x00h\x04eK\x0f]\x94(K\x00h\x04eK\x10]\x94(K\x00h\x04eK\x11]\x94(K\x03h\x02eK\x12]\x94(K\x00h\x04eK\x13]\x94(K\x05h\x02eK\x14]\x94(K\x00h\x04eK\x15]\x94(K\x00h\x04eK\x16]\x94(K\x00h\x04eK\x17]\x94(K\x00h\x04eK\x18]\x94(K\x02h\teu.'

    main()
