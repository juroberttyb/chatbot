import pymongo

client = pymongo.MongoClient("mongodb+srv://juroberttyb:juhome35766970@messages.bixip.mongodb.net/messages?retryWrites=true&w=majority")

msg_db = client.messages
msg_v1 = msg_db.version1

test_data = {
        "nth_chat": 0,
        "chat": {
            "is_client": [False, True], 
            "msg": ["Hi man!", "Fuck you!"], 
            "msg_time": ["0.", " 0.1"]
        }
    }

# insert_many
# msg_v1.insert_one(test_data)

ret = msg_v1.find({"nth_chat":0})
for item in ret:
    print(item)
    print(item["nth_chat"])


