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

def send(msg):
    if len(msg) == 0:
        ret = input("Sure you want to exit? [y|n]:")
        if ret == 'y':
            client.send(b'0' * SIZE)
            exit()
        return

    buflen = str(len(msg))
    buflen = b'0' * (SIZE-len(buflen)) + buflen.encode(FORMAT)
    client.send(buflen)
    client.send(msg.encode(FORMAT))

print("--- Welcome to Robert's Chatbot, you can now chat, or simply press enter to exit, thank you ---")
while True:
    msg = input("Me:")
    send(msg)
