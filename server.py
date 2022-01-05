# from ctypes import sizeof
import socket, threading, json, time

"""[TODO]"""
"""
server perspective
    data format
    {
        nth_chat: int
        chat: 
        {
            is_client: bool array
            msg: str array
            msg_time: float array
        }
    }
"""
"""communication between server and database"""
"""config file for server.py and config file for client.py to simplift code"""
"""should add unit test for functionality testing"""
"""natural language processing toolkit, import nltk"""
"""mutex at 1:model inference time 2:database communication time"""

"""this should be attained by requiring from database once start"""
nth_chat = 0

SIZE = 4
PORT = 5050

#SERVER = "192.168.0.100"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
mutex = threading.Lock()

server_status = True
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[STATUS] server listening on {SERVER}")

def send(msg, conn):
    buflen = str(len(msg))
    buflen = b'0' * (SIZE-len(buflen)) + buflen.encode(FORMAT)
    conn.send(buflen)

    # msg = None
    conn.send(msg.encode(FORMAT))
    return msg

def client_handler(conn, addr):
    """should be removed in future, this var need to be obtained from database"""
    global nth_chat

    print(f"{addr} connected.")

    ### ask for name
    ### create data buffer
    
    mutex.acquire()
    """aquire nth_chat var from database"""
    _nth_chat = nth_chat

    """should update this nth_chat to database"""
    nth_chat += 1
    mutex.release()

    data = {"nth_chat":_nth_chat, "chat":{"is_client":[], "msg":[], "msg_time":[]}}

    """chat time record"""
    start = time.time()
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

        rcv_msg = conn.recv(buflen).decode(FORMAT)
        data["chat"]["is_client"].append(True)
        data["chat"]["msg"].append(rcv_msg)
        data["chat"]["msg_time"].append(time.time()-start)
        print(f"[{addr}] {rcv_msg}")

        ret_msg = send(rcv_msg, conn)
        data["chat"]["is_client"].append(False)
        data["chat"]["msg"].append(ret_msg)
        data["chat"]["msg_time"].append(time.time()-start)
    conn.close()

    end_time = None

    # json.loads() -> load json file
    # json.dumps() -> convert into json
    # with open('person.txt', 'w') as json_file:
    #     json.dump(person_dict, json_file)
    
    data = json.dumps(data)
    print(data)

    """upload data to database"""

while server_status:
    conn, addr = server.accept()
    thread = threading.Thread(target=client_handler, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")
