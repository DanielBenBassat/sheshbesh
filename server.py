import socket
import select
import logging
import protocol
import os

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

LOG_FORMAT = '%(levelname)s | %(asctime)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/server.log'

# 1- white, 2- blue, 0 -none
INITIAL_BOARD = {1: [2, "2"], 2: [0, "0"], 3: [0, "0"], 4: [0, "0"], 5: [0, "0"], 6: [5, "1"],
                 7: [0, "0"], 8: [3, "1"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [5, "2"],
                 13: [5, "1"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [3, "2"], 18: [0, "0"],
                 19: [5, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [0, "0"], 24: [2, "1"],
                 100: [0, "1"],
                 -100: [0, "2"]}


def is_win(board, color):
    """
    checks if the game is over
    :param board: dictionary of the board
    :param color: the color of the player that the function checks if he has won
    :return: true if the player won and false if not
    """
    value = True
    for spot in board.keys():
        if board[spot][1] == color and board[spot][0] > 0:
            value = False
    return value


def main():
    """
    the main function of the server. the server connects to 2 clients and starts the game.
    the server sends the board to each client in his turn and receives it after the changes,
    in each turn the server checks if the client has won
    :return: none
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()
        while True:
            logging.debug("waiting for clients")
            client_sockets = []
            try:
                while len(client_sockets) < 2:
                    rlist, wlist, xlist = select.select([server_socket], [], [])
                    for current_socket in rlist:
                        if len(client_sockets) < 2:
                            connection, client_address = current_socket.accept()
                            logging.debug("new client joined")
                            logging.debug(client_address)
                            client_sockets.append(connection)
                temp = True
                for i in range(2):
                    current_socket = client_sockets[i]
                    func = "1" + str(i + 1)
                    current_socket.send(protocol.send_protocol(func, INITIAL_BOARD))
                    logging.debug(protocol.send_protocol(func, INITIAL_BOARD))
                    func_r, board_r = protocol.receive_protocol(current_socket)
                    logging.debug(protocol.send_protocol(func, INITIAL_BOARD))
                    if func_r != func or board_r != INITIAL_BOARD:
                        temp = False

                current_socket = client_sockets[0]
                color = "1"
                board = INITIAL_BOARD
                if temp:
                    while not is_win(board, color):
                        current_socket.send(protocol.send_protocol("20", board))
                        logging.debug(protocol.send_protocol("20", board))

                        current_socket.settimeout(40)
                        func, board = protocol.receive_protocol(current_socket)
                        logging.debug("received: " + func)

                        if current_socket == client_sockets[0]:
                            color = "1"
                            current_socket = client_sockets[1]
                        else:
                            color = "2"
                            current_socket = client_sockets[0]

                    logging.debug("GAME OVER")
                    func = "3" + str(color)

                    for client_socket in client_sockets:
                        client_socket.send(protocol.send_protocol(func, board))
                        logging.debug("send function: " + func)
                        func_r, board_r = protocol.receive_protocol(client_socket)
                        logging.debug("received function: " + func)
                        if func == func_r and board == board_r:
                            client_socket.close()
                            logging.debug("socket is close")

            except (socket.error, socket.timeout) as e:
                logging.debug(f"Socket error occurred: {e}")
                logging.debug("GAME OVER")
                func = "30"
                count = -1
                try:
                    logging.debug(len(client_sockets))
                    count = 0
                    client_sockets[1].send(protocol.send_protocol(func, board))
                    logging.debug("send function: " + func)

                    count = 1
                    client_sockets[0].send(protocol.send_protocol(func, board))
                    logging.debug("send function: " + func)

                except socket.error as e:
                    logging.debug(f"Socket error occurred: {e}")
                    if count == 0:
                        try:
                            client_sockets[0].send(protocol.send_protocol(func, board))
                            logging.debug("send function: " + func)
                        except socket.error as e:
                            logging.debug(f"Socket error occurred: {e}")

                finally:
                    if count == 0:
                        current_socket = client_sockets[0]
                    else:
                        current_socket = client_sockets[1]
                    func_r, board_r = protocol.receive_protocol(current_socket)
                    logging.debug("received function: " + func)
                    if func == func_r and board == board_r:
                        current_socket.close()
                        logging.debug("socket is close")

            except Exception as e:
                logging.debug(f"An error occurred: {e}")

    except socket.error as err:
        logging.debug('received socket error on server socket' + str(err))

    finally:
        server_socket.close()


if __name__ == "__main__":
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    board1 = {1: [2, "2"], 2: [0, "0"], 3: [0, "0"], 4: [0, "0"], 5: [0, "0"], 6: [5, "1"],
              7: [0, "0"], 8: [3, "1"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [5, "2"],
              13: [5, "1"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [3, "2"], 18: [0, "0"],
              19: [5, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [0, "0"], 24: [2, "1"]}
    assert not is_win(board1, "1")
    assert not is_win(board1, "2")

    board2 = {1: [2, "2"], 2: [0, "0"], 3: [0, "0"], 4: [0, "0"], 5: [0, "0"], 6: [0, "0"],
              7: [0, "0"], 8: [0, "0"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [5, "2"],
              13: [0, "0"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [3, "2"], 18: [0, "0"],
              19: [5, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [0, "0"], 24: [0, "0"]}
    assert is_win(board2, "1")

    assert protocol.send_protocol("11", board1) == b'11262!\x80\x04\x95\xfb\x00\x00\x00\x00\x00\x00\x00}\x94(K\x01]\x94(K\x02\x8c\x012\x94eK\x02]\x94(K\x00\x8c\x010\x94eK\x03]\x94(K\x00h\x04eK\x04]\x94(K\x00h\x04eK\x05]\x94(K\x00h\x04eK\x06]\x94(K\x05\x8c\x011\x94eK\x07]\x94(K\x00h\x04eK\x08]\x94(K\x03h\teK\t]\x94(K\x00h\x04eK\n]\x94(K\x00h\x04eK\x0b]\x94(K\x00h\x04eK\x0c]\x94(K\x05h\x02eK\r]\x94(K\x05h\teK\x0e]\x94(K\x00h\x04eK\x0f]\x94(K\x00h\x04eK\x10]\x94(K\x00h\x04eK\x11]\x94(K\x03h\x02eK\x12]\x94(K\x00h\x04eK\x13]\x94(K\x05h\x02eK\x14]\x94(K\x00h\x04eK\x15]\x94(K\x00h\x04eK\x16]\x94(K\x00h\x04eK\x17]\x94(K\x00h\x04eK\x18]\x94(K\x02h\teu.'
    assert protocol.send_protocol("20", board1) == b'20262!\x80\x04\x95\xfb\x00\x00\x00\x00\x00\x00\x00}\x94(K\x01]\x94(K\x02\x8c\x012\x94eK\x02]\x94(K\x00\x8c\x010\x94eK\x03]\x94(K\x00h\x04eK\x04]\x94(K\x00h\x04eK\x05]\x94(K\x00h\x04eK\x06]\x94(K\x05\x8c\x011\x94eK\x07]\x94(K\x00h\x04eK\x08]\x94(K\x03h\teK\t]\x94(K\x00h\x04eK\n]\x94(K\x00h\x04eK\x0b]\x94(K\x00h\x04eK\x0c]\x94(K\x05h\x02eK\r]\x94(K\x05h\teK\x0e]\x94(K\x00h\x04eK\x0f]\x94(K\x00h\x04eK\x10]\x94(K\x00h\x04eK\x11]\x94(K\x03h\x02eK\x12]\x94(K\x00h\x04eK\x13]\x94(K\x05h\x02eK\x14]\x94(K\x00h\x04eK\x15]\x94(K\x00h\x04eK\x16]\x94(K\x00h\x04eK\x17]\x94(K\x00h\x04eK\x18]\x94(K\x02h\teu.'

    main()
