import socket
import select
import pickle
MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'

# 1- white, 2- blue, 0 -none
INITIAL_BOARD = {1: [2, 2], 2: [0, 0], 3: [0, 0], 4: [0, 0], 5: [0, 0], 6: [5, 1],
                 7: [0, 0], 8: [3, 1], 9: [0, 0], 10: [0, 0], 11: [0, 0], 12: [5, 2],
                 13: [5, 1], 14: [0, 0], 15: [0, 0], 16: [0, 0], 17: [3, 2], 18: [0, 0],
                 19: [5, 2], 20: [0, 0], 21: [0, 0], 22: [0, 0], 23: [0, 0], 24: [2, 1]}

def IsWin():
    return False


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    client_sockets = []

    while len(client_sockets) < 2:
        rlist, wlist, xlist = select.select([server_socket], [], [])
        for current_socket in rlist:
            if len(client_sockets) < 2:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(connection)

    for i in range(2):
        current_socket = client_sockets[i]
        player = str(i + 1)
        current_socket.send(player.encode())

        board= pickle.dumps(INITIAL_BOARD)
        current_socket.send(board)

    current_socket = client_sockets[0]
    while not IsWin():
        current_socket.send(board)
        response = current_socket.recv(1024)
        board = pickle.loads(response)

        if current_socket == client_sockets[0]:
            current_socket = client_sockets[1]
        else:
            current_socket = client_sockets[0]













if __name__ == "__main__":
    main()
