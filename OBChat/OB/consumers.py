import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


from OB.commands.command_handler import handle_command
from .enums import GroupTypes, SystemOperations
from .models import Room
from .utilities import get_group_name, is_command, send_chat_message

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

        room_query = Room.objects.get(name=self.room_name)
        room_query.occupants.add(self.user)
        room_query.save()

        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def send(self, text_data=None, bytes_data=None, close=False):
        super().send(text_data, bytes_data, close)

        message = json.loads(text_data)["message"]

        if is_command(message):
            handle_command(message, self.user, self.room_name)

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        send_chat_message(message, self.room_group_name)

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
