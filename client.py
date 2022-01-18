import socket, threading

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
SERVER = "172.17.0.2"
ADDR = (SERVER, PORT)
SIZE = 4

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def server_msg_handler():
    while True:
        buflen = client.recv(SIZE).decode(FORMAT)

        try:
            buflen = int(buflen)
        except:
            break
        
        if buflen > 8192 or buflen == 0:
            break

        msg = client.recv(buflen).decode(FORMAT)
        print(f"Robert:{msg}")
    client.close()

def send(msg):
    try:
        buflen = str(len(msg))
        buflen = b'0' * (SIZE-len(buflen)) + buflen.encode(FORMAT)
        client.send(buflen)
        client.send(msg.encode(FORMAT))
        return False
    except:
        return True

threading.Thread(target=server_msg_handler).start()

print("--- Welcome to Robert's Chatbot, you can now chat, or simply press enter to exit, thank you ---")
while True:
    msg = input()
    if len(msg) == 0:
        ret = input("Sure you want to exit? [y|n]:")
        if ret == 'y':
            client.send(b'0' * SIZE)
            exit("chatbot is closed")

    """if something went wrong in sending msg"""
    if send(msg):
        exit("connection failed")
