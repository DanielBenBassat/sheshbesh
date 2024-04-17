import pickle


def send_protocol(func, board):
    msg = func.encode()
    board_bytes = pickle.dumps(board)
    length = str(len(board_bytes))
    msg += length.encode() + b'!' + board_bytes
    return msg


def receive_protocol(current_socket):
    func = current_socket.recv(1).decode()
    if func != '':
        func += current_socket.recv(1).decode()

        length = ''
        b = current_socket.recv(1).decode()
        while b != '!':
            length += b
            b = current_socket.recv(1).decode()

        length = int(length)
        board = b''
        for i in range(length):
            board += current_socket.recv(1)

        board = pickle.loads(board)
    else:
        func, board = "-1", "-1"

    return func, board
