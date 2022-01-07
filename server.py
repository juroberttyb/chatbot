"""[TODO]"""
"""
server perspective
    data cfg.get('msg_format')
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
"""add readme"""
"""make this python project like, eg: add __init__.py"""
"""add redis key-value database to save model checkpoint"""

import argparse
parser = argparse.ArgumentParser(description='mode setting')
parser.add_argument('--cfg_path', default="default.cfg", help='path to server configuration file')
args = parser.parse_args()

import configparser
cfg = configparser.ConfigParser()
cfg.read_file(open('default.cfg'))
cfg = cfg['DEFAULT']

def send(msg, conn):
    buflen = str(len(msg))
    buflen = b'0' * (cfg.getint('header_size')-len(buflen)) + buflen.encode(cfg.get('msg_format'))
    conn.send(buflen)

    # msg = None
    conn.send(msg.encode(cfg.get('msg_format')))
    return msg

import time, numpy as np
def client_handler(conn, addr, mutex):
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
        buflen = conn.recv(cfg.getint('header_size')).decode(cfg.get('msg_format'))
        ### print(f"buffer of size {buflen} rcved")
        
        try:
            buflen = int(buflen)
        except:
            print(f"buflen not of type int, {addr} closed")
            break
        
        if buflen > 8192 or buflen == 0:
            print(f"buflen over 8192, {addr} closed")
            break

        rcv_msg = conn.recv(buflen).decode(cfg.get('msg_format'))
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

if cfg.getboolean("reset_db"):
    msg_v1.delete_many({})
    msg_v1.insert_one({"_id": "nth", "nth": 0})
    print("[DATABASE] reset successfully")

import socket
#SERVER = "192.168.0.100"
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, cfg.getint('server_port'))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[STATUS] server listening on {SERVER_IP}")

import threading
mutex = threading.Lock()

while cfg.getboolean('server_status'):
    conn, addr = server.accept()
    thread = threading.Thread(target=client_handler, args=(conn, addr, mutex))
    thread.start()
    print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")
server.close()
