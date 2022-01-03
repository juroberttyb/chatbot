import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "172.17.0.2"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

"""
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    print(len(send_length))
    # pad space to expected header length
    send_length +=  b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    ret = client.recv(2048).decode(FORMAT)
    print(ret)
"""

def send(msg):
    client.send(msg.encode(FORMAT))

while True:
    msg = input("Enter your value: ")
    print(type(msg), msg)
    send(msg)
