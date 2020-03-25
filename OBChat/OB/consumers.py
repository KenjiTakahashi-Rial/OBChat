import json
from enum import Enum

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

# TODO: Move these around so they're more organized
class GroupTypes(Enum):
    Invalid = 0
    Line = 1
    Room = 2
    Private = 3

def group_name(group_type, name, second_name=""):
    switch = {
        GroupTypes.Invalid: name,
        GroupTypes.Line: f"OBLine_{name}",
        GroupTypes.Room: f"room_{name}",
        GroupTypes.Private: f"{min(name, second_name)}_{max(name, second_name)}"
    }

    return switch[group_type]

class ChatConsumer(WebsocketConsumer):
    room_name = None
    room_group_name = None

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        if self.room_name == "OBLine":
            # TODO: Get username from url
            self.room_group_name = group_name(GroupTypes.Line, "username")
        else:
            self.room_group_name = group_name(GroupTypes.Room, self.room_name)

        # Join room group
        async_to_sync(self.channel_layer.group_add) (
            self.room_group_name,
            self.channel_name
        )

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
                "type": "receive_from_group",
                "message": message
            }
        )

    # Receive messages from room group
    def receive_from_group(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "message": message
        }))
