# from ctypes import sizeof
import socket, threading, json, time, argparse, numpy as np

parser = argparse.ArgumentParser(description='mode setting')
parser.add_argument('--reset_db', default=False, help='whether to reset database')
parser.add_argument('--cfg_path', default=None, help='path to server configuration file')
args = parser.parse_args()

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
"""chatbot model"""
"""chatbot model aquire data from db and train"""
"""config file for server.py and config file for client.py to simplift code"""
"""should add unit test for functionality testing"""
"""natural language processing toolkit, import nltk"""
"""mutex at 1:model inference time 2:database communication time"""

"""server configuration to mongodb"""
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
    print(f"{addr} connected.")

    ### ask for name
    ### create data buffer
    
    mutex.acquire()
    """aquire nth from database"""
    nth = msg_v1.find_one({"_id": "nth"})["nth"]
    """update nth to database"""
    msg_v1.update_one({"_id": "nth"}, {"$inc": {"nth": 1}})
    mutex.release()

    data = {
        "nth_chat": nth, 
        "chat": {
            "is_client": [],
            "msg": [],
            "msg_time": []
            }
        }

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
        data["chat"]["msg_time"].append(np.float32(time.time()-start))
        print(f"[{addr}] {rcv_msg}")

        ret_msg = send(rcv_msg, conn)
        data["chat"]["is_client"].append(False)
        data["chat"]["msg"].append(ret_msg)
        data["chat"]["msg_time"].append(np.float32(time.time()-start))
    conn.close()

    end_time = None

    # json.loads() -> load json file
    # json.dumps() -> convert into json
    # data = json.dumps(data)
    # with open('person.txt', 'w') as json_file:
    #     json.dump(person_dict, json_file)

    try:
        """upload data to database"""
        msg_v1.insert_one(data)
    except:
        msg_v1.delete_one({"nth_chat": nth})

import pymongo
mongo_client = pymongo.MongoClient("mongodb+srv://juroberttyb:juhome35766970@messages.bixip.mongodb.net/messages?retryWrites=true&w=majority")
msg_v1 = mongo_client.messages.version1

if args.reset_db:
    msg_v1.delete_many({})
    msg_v1.insert_one({"_id": "nth", "nth": 0})

"""attain server config from mongodb here"""
server_config = {
    "buffer_byte_size": 4,
    "server_port": 5050,
    "server_ip": socket.gethostbyname(socket.gethostname()),
    "message_format": 'utf-8',
    "chat": {
        "is_client": [],
        "msg": [],
        "msg_time": []
        }
    }

while server_status:
    conn, addr = server.accept()
    thread = threading.Thread(target=client_handler, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")
