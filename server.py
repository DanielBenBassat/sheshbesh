import socket
import select
import pickle

import protocol

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

# 1- white, 2- blue, 0 -none
INITIAL_BOARD = {1: [2, "2"], 2: [0, "0"], 3: [0, "0"], 4: [0, "0"], 5: [0, "0"], 6: [5, "1"],
                 7: [0, "0"], 8: [3, "1"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [5, "2"],
                 13: [5, "1"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [3, "2"], 18: [0, "0"],
                 19: [5, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [0, "0"], 24: [2, "1"]}

INITIAL_BOARD = {1: [0, "2"], 2: [0, "0"], 3: [0, "0"], 4: [0, "0"], 5: [0, "0"], 6: [2, "1"],
                 7: [0, "0"], 8: [0, "1"], 9: [0, "0"], 10: [0, "0"], 11: [0, "0"], 12: [0, "2"],
                 13: [0, "1"], 14: [0, "0"], 15: [0, "0"], 16: [0, "0"], 17: [0, "2"], 18: [0, "0"],
                 19: [0, "2"], 20: [0, "0"], 21: [0, "0"], 22: [0, "0"], 23: [1, "2"], 24: [0, "1"]}


def is_win(board, color):
    """
    check if the game is over
    :param board: dictionary of the board
    :param color: theplayer that the function checks if he has won
    :return: true if the player won and false if not
    """
    value = True
    for spot in board.keys():
        if board[spot][1] == color and board[spot][0] > 0:
            value = False
    return value


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()
        while True:
            client_sockets = []
            try:
                while len(client_sockets) < 2:
                    rlist, wlist, xlist = select.select([server_socket], [], [])
                    for current_socket in rlist:
                        if len(client_sockets) < 2:
                            connection, client_address = current_socket.accept()
                            print("New client joined!", client_address)
                            client_sockets.append(connection)

                for i in range(2):
                    current_socket = client_sockets[i]
                    func = "1" + str(i + 1)
                    current_socket.send(protocol.send_protocol(func, INITIAL_BOARD))

                current_socket = client_sockets[0]
                color = "1"
                board = INITIAL_BOARD

                while not is_win(board, color):
                    current_socket.send(protocol.send_protocol("20", board))

                    func, board = protocol.receive_protocol(current_socket)

                    if current_socket == client_sockets[0]:
                        color = "1"
                        current_socket = client_sockets[1]
                    else:
                        color = "2"
                        current_socket = client_sockets[0]

                print("gameover")
                func = "3" + str(color)
                print(func)
                for client_socket in client_sockets:
                    client_socket.send(protocol.send_protocol(func, board))



            except socket.error as e:
                print(f"Socket error occurred: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")




    except socket.error as err:
        print('received socket error on server socket' + str(err))

    finally:
        server_socket.close()




if __name__ == "__main__":
    main()
