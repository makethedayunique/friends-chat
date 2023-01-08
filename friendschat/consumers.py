import json
import re

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.utils import timezone
from friendschat.models import ChatUser, ChatMessage

from friends.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
import redis

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if "user" not in self.scope or self.scope["user"] is None:
            # If there is no user logged in
            await self.close()
            return
        curr_user = self.scope["user"] # Get the current user
        # Instantiate the redis connection
        self.redis_cli = await sync_to_async(redis.Redis)(REDIS_HOST, REDIS_PORT, password=REDIS_PASSWORD)
        self.redis_key = "user_{}".format(curr_user.id)
        await sync_to_async(self.redis_cli.sadd)(self.redis_key, self.channel_name) # Add the channel to the set
        self.chat_user = await self.__get_google_user(curr_user) # Get the current user
        if self.chat_user is None:
            # Reject the connection
            await self.close()
            return
        print(self.channel_name)
        await database_sync_to_async(self.chat_user.update)(commit=True, is_online=True)
        self.friends_cache = {} # Stores friend id : google user
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """Receive data from client
        
        Validate the data, send the message to self and friend
        """
        if "user" not in self.scope or self.scope["user"] is None:
            await self.close()
            return
        text_data_json = json.loads(text_data)
        if not self.__validate_message_from_cli(text_data_json):
            # Ignore this message
            return
        friend_user_id = text_data_json["friend_box"][22:]
        if friend_user_id in self.friends_cache:
            friend_chat_user = self.friends_cache[friend_user_id]
        else:
            friend_user = await self.__get_user(friend_user_id)
            if friend_user is None:
                # Ignore this message
                return
            friend_chat_user = await self.__get_google_user(friend_user)
            if friend_chat_user is None:
                # Ignore this message
                return
            # Check whether this is current's chat user's friend
            if_friend = await self.__whether_friend(friend_chat_user)
            if not if_friend:
                # Reject this message
                return
            self.friends_cache[friend_user_id] = friend_chat_user # Set the cache
        # Save this message to database
        msg_json = await self.__save_one_message(self.chat_user, friend_chat_user, 
                text_data_json["message"])
        # Send this message to self and friend's layers
        message_to_friend = {
            "type": "chat_onetoone",
            "message_id": msg_json["id"]
        }
        message_to_client = {
            "msg_type": 0,
            "msg_from_self": True,
            "msg_id": msg_json["id"],
            "msg_user": msg_json["send_to"],
            "msg_datetime": msg_json["send_time"],
            "msg": msg_json["send_message"]
        }
        friends_channels = await sync_to_async(self.redis_cli.smembers)("user_" + str(msg_json["send_to"]))
        for fc in friends_channels:
            await self.channel_layer.send(fc.decode(), message_to_friend)
        await self.send(text_data=json.dumps(message_to_client))


    async def disconnect(self, code):
        # Remove this connection from the redis
        sync_to_async(self.redis_cli.srem)(self.redis_key, self.channel_name)

    async def chat_onetoone(self, event):
        msg_id = int(event["message_id"])
        msg_json = await self.__get_one_message(msg_id)
        await self.send(text_data=json.dumps(msg_json))

    @database_sync_to_async
    def __get_google_user(self, user: User):
        """Try to get the google user which is ChatUser of a user"""
        chat_user = None
        try:
            chat_user = ChatUser.objects.get(related_user=user)
        except ChatUser.DoesNotExist:
            pass
        except ChatUser.MultipleObjectsReturned:
            pass
        return chat_user

    @database_sync_to_async
    def __get_user(self, user_id: any):
        """Try to get a user based on the user id
        
        Return None, if there is no such user
        """
        user_id_int = None
        try:
            user_id_int = int(user_id)
        except:
            return None
        user = None
        try:
            user = User.objects.get(id=user_id_int)
        except:
            return None
        return user

    @database_sync_to_async
    def __save_one_message(self, sendFrom: ChatUser, sendTo: ChatUser, content):
        """This function will save one message to the database and return the id"""
        message_key = str(sendFrom.related_user.id) + "_" + str(sendTo.related_user.id)
        chat_msg = ChatMessage(
            message_key=message_key, 
            send_from=sendFrom,
            send_to=sendTo,
            send_message=content,
            send_time=timezone.now()
            )
        chat_msg.save() # Save to database
        msg_json = {
            "id": chat_msg.id,
            "send_to": sendTo.related_user.id,
            "send_message": content,
            "send_time": chat_msg.send_time.isoformat()
        }
        return msg_json

    @database_sync_to_async
    def __get_one_message(self, msg_id: int):
        msg_json = {}
        chat_msg = None
        try:
            chat_msg = ChatMessage.objects.get(id=msg_id)
        except:
            return None
        msg_json["msg_type"] = 0
        msg_json["msg_from_self"] = False
        msg_json["msg_id"] = msg_id
        msg_json["msg_user"] = chat_msg.send_from.related_user.id
        msg_json["msg_datetime"] = chat_msg.send_time.isoformat()
        msg_json["msg"] = chat_msg.send_message
        return msg_json

    @database_sync_to_async
    def __whether_friend(self, some_user: ChatUser):
        """Check whether some user is self user's friend"""
        return self.chat_user.friends.contains(some_user)

    def __validate_message_from_cli(self, message_json: dict) -> bool:
        """This function will validate the message received"""
        if "friend_box" not in message_json or "message" not in message_json:
            return False
        if not re.match(r"^id_chat_inputbox_with_[0-9]+$", message_json["friend_box"]):
            return False
        if message_json["message"] == "":
            return False
        return True


