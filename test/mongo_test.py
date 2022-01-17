import pymongo

client = pymongo.MongoClient("mongodb+srv://juroberttyb:juhome35766970@messages.bixip.mongodb.net/messages?retryWrites=true&w=majority")

msg_db = client.messages
msg_v1 = msg_db.version1

"""
ret = msg_v1.find({})
for item in ret:
    print(item)
"""

#"""
test_data = {
        "nth_chat": 0,
        "chat": {
            "is_client": [False, True], 
            "msg": ["Hi man!", "Fuck you!"], 
            "msg_time": ["0.", " 0.1"]
        }
    }

msg_v1.delete_many({})
msg_v1.insert_one({"_id": "nth", "nth": 0})
msg_v1.update_one({"_id": "nth"}, {"$set": {"nth": 0}})
msg_v1.insert_one(test_data)
# insert_many

data = msg_v1.find_one({"nth_chat": 0})
chat_msg = data["chat"]["msg"]
chat_msg[-1] = "no shit"

msg_v1.update_one({"nth_chat": 0}, {"$set": {"chat.msg": chat_msg}}) # (search criterion, how to change)
# update_many

# {"nth_chat":0} is interpreted as search criterion
msg_v1.delete_one({"nth_chat": 0})

count = msg_v1.count_documents({})
print(f"count:{count}")

ret = msg_v1.find({})
for item in ret:
    print(item)
#"""