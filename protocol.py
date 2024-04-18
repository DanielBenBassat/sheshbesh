import pickle


def send_protocol(func, board):
    """
    gets the func and the board and make the message to send according to the protocol
    :param func:
    :param board:
    :return: the message to send
    """
    if board == "100":
        msg = func + "0" + "!"
    else:
        msg = func.encode()
        board_bytes = pickle.dumps(board)
        length = str(len(board_bytes))
        msg += length.encode() + b'!' + board_bytes

    return msg


def receive_protocol(current_socket):
    """
    receives a message according to the protocol
    :param current_socket: the socket
    :return: func and board that have been received
    """
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





