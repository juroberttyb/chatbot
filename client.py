import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "172.17.0.2"
ADDR = (SERVER, PORT)
SIZE = 4

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
    buflen = str(len(msg))
    buflen = b'0' * (SIZE-len(buflen)) + buflen.encode(FORMAT)
    client.send(buflen)
    client.send(msg.encode(FORMAT))

while True:
    msg = input("msg: ")
    print(type(msg), msg)
    send(msg)
