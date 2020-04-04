import json
from enum import Enum

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Room

# TODO: Move these around so they're more organized
class GroupTypes(Enum):
    Invalid = 0
    Line = 1
    Room = 2
    Private = 3

def get_group_name(group_type, name, second_name=""):
    switch = {
        GroupTypes.Invalid: name,
        GroupTypes.Line: f"OBLine_{name}",
        GroupTypes.Room: f"room_{name}",
        GroupTypes.Private: f"{min(name, second_name)}_{max(name, second_name)}"
    }

    return switch[group_type]

class SystemOperations(Enum):
    Invalid = 0
    Kick = 1

class ChatConsumer(WebsocketConsumer):
    user = None
    room_name = None
    room_group_name = None

    def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        if self.room_name == "OBLine":
            self.room_group_name = get_group_name(GroupTypes.Line, self.user.username)
        else:
            self.room_group_name = get_group_name(GroupTypes.Room, self.room_name)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # TODO: add the user to the room's list of current users

        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message
            }
        )

    # Receive messages from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "message": message
        }))

    def system_operation(self, event):
        if event["operation"] == SystemOperations.Kick and event["user"] == self.user:
            self.close()
