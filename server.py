import argparse
parser = argparse.ArgumentParser(description='mode setting')
parser.add_argument('--config_path', default="config.json", help='path to server configuration file')
parser.add_argument('--key_path', default="key.json", help='path to key file')
args = parser.parse_args()

import json
with open(args.config_path) as config_file:
    cfg = json.load(config_file)
with open(args.key_path) as key_file:
    key = json.load(key_file)

import threading
db_mutex = threading.Lock()
parlai_mutex= threading.Lock()

def send(msg, conn):
    buflen = str(len(msg))
    buflen = b'0' * (cfg['header_size']-len(buflen)) + buflen.encode(cfg['msg_format'])
    conn.send(buflen)

    msg = msg.encode(cfg['msg_format'])
    conn.send(msg)

from parlai.core.teachers import register_teacher, DialogTeacher
@register_teacher("message")
class Messager(DialogTeacher):
    data = None

    def __init__(self, opt, shared=None):
        opt['datafile'] = opt['datatype'].split(':')[0] + ".txt"
        super().__init__(opt, shared)
    
    def setup_data(self):
        for element in self.data:
            yield element

import time, numpy as np
import chatter
def client_handler(conn, addr):
    print(f"{addr} connected.")

    ### ask for name
    ### create data buffer
    
    db_mutex.acquire()
    """aquire nth from database"""
    nth = msg_v1.find_one({"_id": "nth"})["nth"]
    """update nth to database"""
    msg_v1.update_one({"_id": "nth"}, {"$inc": {"nth": 1}})
    db_mutex.release()

    data = {
        "nth_chat": nth, 
        "chat": {
            "is_client": [],
            "msg": [],
            "msg_time": []
            }
        }

    """chat time record"""
    start, first_msg_flag = time.time(), True
    while True:
        buflen = conn.recv(cfg['header_size']).decode(cfg['msg_format'])
        ### print(f"buffer of size {buflen} rcved")
        
        try:
            buflen = int(buflen)
        except:
            print(f"buflen not of type int, {addr} closed")
            break
        
        if buflen > 8192 or buflen == 0:
            print(f"buflen over 8192, {addr} closed")
            break

        rcv_msg = conn.recv(buflen).decode(cfg['msg_format'])
        data["chat"]["is_client"].append(bool(cfg['is_client_flag']))
        data["chat"]["msg"].append(rcv_msg)
        data["chat"]["msg_time"].append(np.float32(time.time()-start))
        print(f"[{addr}] {rcv_msg}")

        parlai_mutex.acquire()
        chatter.Messager.data = [[(rcv_msg, 'hi'), True]]
        ret_msg = chatter.RobertDisplayModel.main(
                                            task='message',
                                            model_file='model/model',
                                            num_examples=1,
                                            skip_generation=False,
                                        )
        parlai_mutex.release()

        send(ret_msg, conn)
        data["chat"]["is_client"].append(not bool(cfg['is_client_flag']))
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
mongo_client = pymongo.MongoClient(f"mongodb+srv://{key['mongodb']['username']}:{key['mongodb']['password']}@messages.bixip.mongodb.net/messages?retryWrites=true&w=majority")
msg_v1 = mongo_client.messages.version1

if cfg['reset_db']:
    msg_v1.delete_many({})
    msg_v1.insert_one({"_id": "nth", "nth": 0})
    print("[DATABASE] reset successfully")

import socket
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, cfg['server_port'])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[STATUS] server listening on {SERVER_IP}")

while bool(cfg['server_status']):
    conn, addr = server.accept()
    thread = threading.Thread(target=client_handler, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")
server.close()
