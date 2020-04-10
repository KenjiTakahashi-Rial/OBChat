import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from OB.commands.command_handler import handle_command
from .enums import GroupTypes, SystemOperations
from .models import Message, Room
from .utilities import get_group_name, is_command, send_room_message

class ChatConsumer(WebsocketConsumer):
    user = None
    room = None
    room_group_name = None

    def connect(self):
        self.user = self.scope["user"]

        room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room = Room.objects.get(name=room_name)

        if self.room.name == f"{self.user.username}-OBLine":
            self.room_group_name = get_group_name(GroupTypes.Line, self.user.username)
        else:
            self.room_group_name = get_group_name(GroupTypes.Room, self.room.name)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        room_query = Room.objects.get(name=self.room.name)
        room_query.occupants.add(self.user)
        room_query.save()

        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Send the message to the client
    # pylint: disable=useless-super-delegation
    # TODO: Revisit this and add to it
    def send(self, text_data=None, bytes_data=None, close=False):
        super().send(text_data, bytes_data, close)

    # Received a message from the client
    # Send it to this consumer's room group
    def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)["message"]

        # Send message to room group
        send_room_message(message, self.user, self.room)

        if  message:
            Message(message=message, sender=self.user, room=self.room).save()

        if is_command(message):
            handle_command(message, self.user, self.room)

    # A message was received by another consumer and sent to a group this consumer is in
    def room_message(self, event):
        # Send message to client
        self.send(text_data=json.dumps({
            "message": event["message"]
        }))

    def system_message(self, event):
        self.send(text_data=json.dumps({
            "message": event["message"]
        }))

    def system_operation(self, event):
        if event["operation"] == SystemOperations.Kick and event["user"] == self.user:
            self.close()
