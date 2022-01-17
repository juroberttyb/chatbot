import argparse, json, threading, chatter, time, pymongo, socket, numpy as np

parser = argparse.ArgumentParser(description='mode setting')
parser.add_argument('--configs_dir', default="configs", help='path to configs')
parser.add_argument('--config_path', default="config.json", help='path to server configuration file')
parser.add_argument('--key_path', default="key.json", help='path to key file')
args = parser.parse_args()

with open(f"{args.configs_dir}/{args.config_path}") as config_file:
    cfg = json.load(config_file)
with open(f"{args.configs_dir}/{args.key_path}") as key_file:
    key = json.load(key_file)

mongo_mutex = threading.Lock()
model_mutex= threading.Lock()

def send(msg, conn):
    buflen = str(len(msg))
    buflen = b'0' * (cfg['header_size']-len(buflen)) + buflen.encode(cfg['msg_format'])
    conn.send(buflen)

    msg = msg.encode(cfg['msg_format'])
    conn.send(msg)

def client_handler(conn, addr):
    print(f"{addr} connected.")

    mongo_mutex.acquire()
    """[DATABASE] aquire and update global nth"""
    nth = msg_v1.find_one({"_id": "nth"})["nth"]
    msg_v1.update_one({"_id": "nth"}, {"$inc": {"nth": 1}})
    mongo_mutex.release()

    data = dict(cfg['document_format'])
    data['nth_chat'] = nth

    start, is_first_msg = time.time(), True
    send("Hi, please tell me your name, or type [DEFAULT] to be treated as default.", conn)
    while True:
        buflen = conn.recv(cfg['header_size']).decode(cfg['msg_format'])

        try:
            buflen = int(buflen)
        except:
            print(f"buflen not of type int, {addr} closed")
            break
        
        if buflen > 8192 or buflen == 0:
            print(f"buflen over 8192, {addr} closed")
            break

        rcv_msg = conn.recv(buflen).decode(cfg['msg_format'])
        if is_first_msg:
            is_first_msg = False
            print(f"|{rcv_msg}|")
            ret = msg_v1.find_one({"username": rcv_msg})
            if ret is not None:
                data = ret
                send(f"Nice to see you again {rcv_msg}, we can now chat.", conn)
            else:
                data['username'] = rcv_msg
                send(f"Nice to meet you {rcv_msg}, we can now chat.", conn)
            
            history = [[[data["chat"]["msg"][i]], True] if i==0 \
                        else [[data["chat"]["msg"][i]], False] \
                        for i in range(0, len(data["chat"]["msg"]), 2)
                    ]
            continue
        else:
            data["chat"]["is_client"].append(bool(cfg['is_client_flag']))
            data["chat"]["msg"].append(rcv_msg)
            data["chat"]["msg_time"].append(round(time.time()-start, 2))
            # print(f"[{addr}] {rcv_msg}")

        if len(history) > 0:
            history += [[[rcv_msg], False]]
        else:
            history = [[[rcv_msg], True]]
        # print(history)

        model_mutex.acquire()
        chatter.Messager.data = history # [history[-1]]
        
        ret_msg = chatter.RobertDisplayModel.main(
                                            task='message',
                                            model_file='model/model',
                                            num_examples=len(history),
                                            skip_generation=False,
                                        )[-1] # [-1] # -1 for latest return message
        model_mutex.release()

        # print(ret_msg)
        # ret_msg = ret_msg[-1]
        send(ret_msg, conn)
        data["chat"]["is_client"].append(not bool(cfg['is_client_flag']))
        data["chat"]["msg"].append(ret_msg)
        data["chat"]["msg_time"].append(round(time.time()-start, 2))
    conn.close()

    try:
        msg_v1.insert_one(data)
    except Exception as exception:
        msg_v1.delete_one({"nth_chat": nth})
        print(f"insert failed, data deleted. {exception}")

mongo_client = pymongo.MongoClient(f"mongodb+srv://{key['mongodb']['username']}:{key['mongodb']['password']}@messages.bixip.mongodb.net/messages?retryWrites=true&w=majority")
msg_v1 = mongo_client.messages.version1

if cfg['reset_db']:
    msg_v1.delete_many({})
    msg_v1.insert_one({"_id": "nth", "nth": 0})
    print("[DATABASE] reset successfully")

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
