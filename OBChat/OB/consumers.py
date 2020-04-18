"""
Consumers manage OBChat's WebSocket communication.

See the Django Channels documentation on Consumers for more information.
https://channels.readthedocs.io/en/latest/topics/consumers.html
"""

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from OB.commands.command_handler import handle_command
from OB.constants import GroupTypes
from OB.models import Message, Room
from OB.utilities.command import is_command
from OB.utilities.event import send_room_message
from OB.utilities.format import get_datetime_string, get_group_name

class OBConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        """
        Description:
            Defines the instance variables for this consumer's user, room, and room_group_name.
            A user may be referenced by only one OBConsumer.
            A room may be referenced by many OBConsumers.

        Arguments:
            self (OBConsumer)

        Return values:
            None
        """

        self.user = None
        self.room = None
        self.room_group_name = None

        super().__init__(*args, **kwargs)

    ###############################################################################################
    # Connection Methods                                                                          #
    ###############################################################################################

    def connect(self):
        """
        Description:
            Set the data for a consumer before it accepts an incoming WebSocket.
            Add the OBConsumer's user reference to the OBConsumer's room reference's list of
            occupants.

        Arguments:
            self (OBConsumer)

        Return values:
            None
        """

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

        # Add to the occupants list for this room
        room_object = Room.objects.get(name=self.room.name)
        room_object.occupants.add(self.user)

        self.accept()

    def disconnect(self, code):
        """
        Description:
            Leaves the Room group that this consumer was a part of. It will no longer send to or
            receive from that group. 
            Remove the OBConsumer's user reference to the OBConsumer's room reference's list of
            occupants.
            Called when a WebSocket connection is closed.

        Arguments:
            self (OBConsumer)
            code: A disconnect code to indicate disconnect conditions

        Return values:
            None
        """

        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

        print(f"WebSocket disconnected with code {code}.")

        # Remove from the occupants list for this room
        room_object = Room.objects.get(name=self.room.name)
        room_object.occupants.remoe(self.user)

    ###############################################################################################
    # Messaging Methods                                                                           #
    ###############################################################################################

    # pylint: disable=useless-super-delegation
    # It's possible this overridden function will be required later on
    def send(self, text_data=None, bytes_data=None, close=False):
        """
        Description:
            ...

        Arguments:
            ...

        Return values:
            ...
        """

        super().send(text_data, bytes_data, close)

    def receive(self, text_data=None, bytes_data=None):
        """
        Description:
            Received a decoded WebSocket frame from the client, NOT from another consumer in this
            consumers group.
            Only the consumer whose user sent the message will call this method.
            This is called first in the process of sending a message.
            Finally, if the message is acommand (see is_command()), then handle it.

        Arguments:
            self (OBConsumer)
            text_data (string): A JSON string containing the message text. Constructed in the
            JavaScript of room.html.
            bytes_data: Not used yet, but will contain images or other message contents which
                cannot be represented by text.

        Return values:
            None
        """

        # Skip empty messages
        if not text_data and not bytes_data:
            return

        # Decode the JSON
        message_text = json.loads(text_data)["message_text"]

        # Save message to database
        new_message_object = Message(message=message_text, sender=self.user, room=self.room)
        new_message_object.save()

        # Encode the message data and metadata
        message_json = json.dumps({
            "text": message_text,
            "sender": self.user.display_name or self.user.username,
            "timestamp": get_datetime_string(new_message_object.timestamp)
        })

        # Send message to room group
        send_room_message(message_json, self.room.name)

        # Handle command
        if is_command(text_data):
            handle_command(text_data, self.user, self.room)

    ###############################################################################################
    # Event Handler Methods                                                                       #
    ###############################################################################################

    def room_message(self, event):
        """
        Description:
            An event of type "room_message" was sent to a group this consumer is a part of.
            Send the message JSON to the client associated with this consumer.

        Arguments:
            self (OBConsumer)
            event (dict): Contains the message JSON

        Return values:
            None
        """

        self.send(text_data=event["message_json"])

    def kick(self, event):
        """
        Description:
            An event of type "kick" was sent to a group this consumer is a part of.
            Perform actions depending on if the user associated with this consumer is specified.

        Arguments:
            self (OBConsumer)
            event (dict): Contains the target user

        Return values:
            None
        """

        if event["target"] == self.user:
            self.close()
