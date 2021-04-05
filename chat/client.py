import socket

PORT = 5555
SERVER = "192.168.1.146"
ADDRESS = (SERVER, PORT)
HEADER = 2048
DISCONNECT_MSG = "!disconnect"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

def send(msg):
    message = msg.encode("UTF-8")
    msg_length = len(message)
    send_length = str(msg_length).encode("UTF-8")
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

send("Hello World!")
input()
send("We are getting somewhere!")
input()
send(DISCONNECT_MSG)