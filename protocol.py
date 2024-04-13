import pickle
INITIAL_BOARD = {1: [2, 2], 2: [0, 0], 3: [0, 0], 4: [0, 0], 5: [0, 0], 6: [5, 1],
                  7: [0, 0], 8: [3, 1], 9: [0, 0], 10: [0, 0], 11: [0, 0], 12: [5, 2],
                  13: [5, 1], 14: [0, 0], 15: [0, 0], 16: [0, 0], 17: [3, 2], 18: [0, 0],
                  19: [5, 2], 20: [0, 0], 21: [0, 0], 22: [0, 0], 23: [0, 0], 24: [2, 1]}
def send_board(board):
    boardBytes= pickle.dumps(board)
    length = str(len(boardBytes))
    msg = length.encode() + b'!' + boardBytes
    return msg

print(send_board(INITIAL_BOARD))


def receive_board(current_socket):
    length = ''
    b = current_socket.recv(1).decode()
    if b != '':
        while b != '!':
            length += b
            b = current_socket.recv(1).decode()

        length= int(length)
        dict = b''
        for i in range(length):
            dict += current_socket.recv(1)

        dict= pickle.loads(dict)
        return dict
    return -1







