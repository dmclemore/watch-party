import socket
import threading

PORT = 5555
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
HEADER = 2048
DISCONNECT_MSG = "!disconnect"

# create server socket and bind it to the server address
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def handle_client(connection, address):
    print(f"[NEW CONNECTION] {address} connected.")

    connected = True
    while connected:
        msg_length = connection.recv(HEADER).decode("UTF-8")
        if msg_length:
            msg_length = int(msg_length)
            msg = connection.recv(msg_length).decode("UTF-8")
            if msg == DISCONNECT_MSG:
                connected = False

            print(f"[{address}] {msg}")
    
    connection.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        connection, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

print("[STARTING] Server is starting.")
start()