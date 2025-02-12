import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from pymongo import MongoClient
from jwt.exceptions import InvalidTokenError
import datetime
import random
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../application_gas_utility/.env')

MONGO_URI = str(os.getenv('MONGODB_URI'))
client = MongoClient(MONGO_URI)
db = client['cluster']
users_collection = db['users']
conversations_collection = db['conversations']
message_queue_collection = db['message_queue']


SECRET_KEY = str(os.getenv('JWT_SECRET_KEY'))
JWT_ALGORITHM = "HS256"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self, text_data):
        data = json.loads(text_data)
        jwt_token = data.get("jwt_token")
        
        if not jwt_token:
            await self.close(code=4001)
            return
        
        decoded_token = jwt.decode(jwt_token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        self.username =  decoded_token.get("username")
        self.user_type =  decoded_token.get("user_type")
        
        user_data = users_collection.find_one({"username": self.username}) 
        print(user_data)
        
        if not user_data:
            await self.close(code=4002)
            return
        
        if self.user_type == "normal":
            
            
            if_user = conversations_collection.find_one({"username": self.username}) 
            if not if_user:

                support_users = list(users_collection.find({"user_type": "support"}))
                if not support_users:
                    await self.send(json.dumps({"error": "No customer support available"}))
                    await self.close(code=4004)
                    return
                
                support_user = random.choice(support_users)
                self.support_username = support_user["username"]

                conversations_collection.update_one(
                    {"user": self.username, "support_user": self.support_username},
                    {"$set": {"created_at": datetime.datetime.utcnow()}},
                    upsert=True
                )
            else:
                self.support_username = if_user["support_user"]
        else:
            self.support_username = None
        
        await self.accept()

        print( "hell: ",self.username )
        pending_messages = list(message_queue_collection.find({"receiver": self.username}))
        for message in pending_messages:
            await self.send(json.dumps({
                "sender": message["sender"],
                "message": message["message"]
            }))
            message_queue_collection.delete_one({"_id": message["_id"]})
        
            
    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")

        if self.user_type == "normal":
            conversation = conversations_collection.find_one({"user": self.username})
            if not conversation:
                await self.send(json.dumps({"error": "No assigned support agent found"}))
                return
            receiver = conversation["support_user"]
        else:
            receiver = data.get("receiver")
            if not receiver:
                active_conversation = conversations_collection.find_one({"support_user": self.username})
                if active_conversation:
                    receiver = active_conversation["user"]
                else:
                    await self.send(json.dumps({"error": "No customer specified or active conversation found"}))
                    return
            conversation = conversations_collection.find_one({"user": receiver, "support_user": self.username})
            if not conversation:
                await self.send(json.dumps({"error": "No customer specified or active conversation found"}))
                return
        
        if receiver in self.channel_layer.groups:
            await self.channel_layer.group_send(
                receiver,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.username
                }
            )
        else:
            message_queue_collection.insert_one({
                "sender": self.username,
                "receiver": receiver,
                "message": message,
                "timestamp": datetime.datetime.utcnow()
            })


    async def chat_message(self, event):
        await self.send(json.dumps({
            "sender": event["sender"],
            "message": event["message"]
        }))
