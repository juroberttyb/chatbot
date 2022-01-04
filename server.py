from ctypes import sizeof
import socket, threading

"""should add unit test for functionality testing"""
"""natural language processing toolkit, import nltk"""
"""mutex"""

"""
mutex = threading.Lock()
mutex.acquire()
try:
    print('Do some stuff')
finally:
    mutex.release()
"""

SIZE = 4
PORT = 5050

#SERVER = "192.168.0.100"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

server_status = True
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[STATUS] server listening on {SERVER}")

def send(msg, conn):
    buflen = str(len(msg))
    buflen = b'0' * (SIZE-len(buflen)) + buflen.encode(FORMAT)
    conn.send(buflen)
    conn.send(msg.encode(FORMAT))

def client_handler(conn, addr):
    print(f"{addr} connected.")

    while True:
        buflen = conn.recv(SIZE).decode(FORMAT)
        ### print(f"buffer of size {buflen} rcved")
        
        try:
            buflen = int(buflen)
        except:
            print(f"buflen not of type int, {addr} closed")
            break
        
        if buflen > 8192 or buflen == 0:
            print(f"buflen over 8192, {addr} closed")
            break

        msg = conn.recv(buflen).decode(FORMAT)
        print(f"[{addr}] {msg}")
        send(msg, conn)
    conn.close()

while server_status:
    conn, addr = server.accept()
    thread = threading.Thread(target=client_handler, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")
