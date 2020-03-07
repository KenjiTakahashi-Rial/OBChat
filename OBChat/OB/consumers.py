import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        
        if self.room_name == "OBLine":
            # TODO: Get username from url
            self.room_group_name = "OBLine_username"
        else:
            self.room_group_name = f"room_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add) (
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard) (
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send) (
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
