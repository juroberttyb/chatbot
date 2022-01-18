import argparse, json, threading, chatter, time, pymongo, socket, redis, pickle, copy

parser = argparse.ArgumentParser(description='mode setting')
parser.add_argument('--configs_dir', default="configs", help='path to configs')
parser.add_argument('--config_path', default="config.json", help='path to server configuration file')
parser.add_argument('--key_path', default="key.json", help='path to key file')
args = parser.parse_args()

with open(f"{args.configs_dir}/{args.config_path}") as config_file:
    cfg = json.load(config_file)
with open(f"{args.configs_dir}/{args.key_path}") as key_file:
    key = json.load(key_file)

mongo_mtx = threading.Lock()
model_mtx= threading.Lock()

def send(msg, conn):
    buflen = str(len(msg))
    buflen = b'0' * (cfg['header_size']-len(buflen)) + buflen.encode(cfg['msg_format'])
    conn.send(buflen)

    msg = msg.encode(cfg['msg_format'])
    conn.send(msg)

def client_handler(conn, addr):
    print(f"{addr} connected.")

    start = None
    send("Welcome, please tell me your name.", conn)
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
        if start is None:
            mongo_ret = mongo_msg.find_one({"username": rcv_msg})
            if mongo_ret is not None:
                data = mongo_ret
                byte_obj = redis_msg.get(data["username"])
                data["chat"]["msg"] = pickle.loads(byte_obj)
                send(f"Nice to see you again {rcv_msg}.", conn)
            else:
                data = copy.deepcopy(cfg['document_format'])
                data['username'] = rcv_msg
                send(f"Nice to meet you {rcv_msg}.", conn)
            
            history = [[[data["chat"]["msg"][i]], i==0] \
                         for i in range(0, len(data["chat"]["msg"]), 2)
                    ]

            start = time.time()
            continue
        else:
            data["chat"]["is_client"].append(bool(cfg['is_client_flag']))
            data["chat"]["msg"].append(rcv_msg)
            data["chat"]["msg_time"].append(round(time.time()-start, 2))

        if len(history) > 0:
            history += [[[rcv_msg], False]]
        else:
            history = [[[rcv_msg], True]]

        num_memory = 2
        model_mtx.acquire()
        chatter.Messager.data = history[-num_memory:] # history
        
        ret_msg = chatter.RobertDisplayModel.main(
                                            task='message',
                                            model_file='model/model',
                                            num_examples=num_memory, # len(history),
                                            skip_generation=False,
                                        )[-1] # -1 for latest return message
        model_mtx.release()

        send(ret_msg, conn)
        data["chat"]["is_client"].append(not bool(cfg['is_client_flag']))
        data["chat"]["msg"].append(ret_msg)
        data["chat"]["msg_time"].append(round(time.time()-start, 2))
    conn.close()

    mongo_mtx.acquire()
    nth = mongo_msg.find_one({"_id": "nth"})["nth"]
    mongo_msg.update_one({"_id": "nth"}, {"$inc": {"nth": 1}})
    mongo_mtx.release()

    if start is not None:
        msgs = data["chat"].pop('msg', None)
        redis_msg.set(data["username"], pickle.dumps(msgs))
        if mongo_ret is None:
            data["nth_chat"] = nth
            mongo_msg.insert_one(data)
        else:
            mongo_msg.update_one({"username": data["username"]}, {"$set" : {
                                                                    "nth_chat":  nth,
                                                                    "chat.is_client" : data["chat"]["is_client"],
                                                                    # "chat.msg" : data["chat"]["msg"],
                                                                    "chat.msg_time" : data["chat"]["msg_time"]
                                                                    }})

mongo_client = pymongo.MongoClient(f"mongodb+srv://{key['mongodb']['username']}:{key['mongodb']['password']}@messages.bixip.mongodb.net/messages?retryWrites=true&w=majority")
mongo_msg = mongo_client.messages.version1
redis_msg = redis.Redis(host='redis-10145.c258.us-east-1-4.ec2.cloud.redislabs.com', port=10145, db=0, password=key['redis']['password'])

if cfg['reset_db']:
    mongo_msg.delete_many({})
    mongo_msg.insert_one({"_id": "nth", "nth": 0})

    for key in redis_msg.scan_iter("*"):
        print(f"key {key.decode('utf-8')} deleted")
        redis_msg.delete(key)
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
