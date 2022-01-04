from ctypes import sizeof
import socket
import threading

""" Feature: transfer protocol design (length, content, end_signal) """
""" Feature: send object using pickle lib (eg: json...) """
""" Feature: large file transfer """
""" Feature: file management """
""" Feature: online chat room """
""" Feature: global message pool (list of msg to be sent from i to j) """
""" Feature: cross platform (PC, mobile...) online chat room """
""" Feature: website based file management sys (like google storage) """
""" Feature: Oracle """

"""
natural language processing toolkit
import nltk
"""

SIZE = 4
PORT = 5050

#SERVER = "192.168.0.100"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

def handle_client(conn, addr):
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

        # conn.send("shut the fuck up".encode(FORMAT))
    conn.close()

server_status = True
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[STATUS] server listening on {SERVER}")

while server_status:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")
