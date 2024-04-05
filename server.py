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


def IsWin(board: dict, color: int):
    if not isinstance(color, int):
        return '-1'
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

            board = pickle.dumps(INITIAL_BOARD)
            current_socket.send(board)
            response = current_socket.recv(1024).decode()
            print(response)

        current_socket = client_sockets[0]
        color = 1
        board = INITIAL_BOARD
        boardBytes= pickle.dumps(board)
        while not IsWin(board, color):
            current_socket.send(boardBytes)
            response = current_socket.recv(1024)
            boardBytes = response
            board = pickle.loads(boardBytes)

            if current_socket == client_sockets[0]:
                color =1
                current_socket = client_sockets[1]
            else:
                color =2
                current_socket = client_sockets[0]

        print("game over" )

    except socket.error as e:
        print(f"Socket error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        server_socket.close()
        for client_socket in client_sockets:
            client_socket.close()

if __name__ == "__main__":
    main()
