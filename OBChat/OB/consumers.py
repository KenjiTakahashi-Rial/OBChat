"""
Consumers manage OBChat's WebSocket communication.

See the Django Channels documentation on Consumers for more information.
https://channels.readthedocs.io/en/latest/topics/consumers.html
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer

from OB.commands.command_handler import handle_command
from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import Message, OBUser, Room
from OB.utilities.command import is_command
from OB.utilities.database import sync_add, sync_delete, sync_get, sync_remove, sync_save, try_get
from OB.utilities.event import send_room_message
from OB.utilities.format import get_datetime_string, get_group_name

class OBConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        """
        Description:
            Defines the instance variables for this consumer's session, user, and room.
            The session and user are unique to each OBConsumer.
            The room is not unique.

        Arguments:
            self (OBConsumer)

        Return values:
            None
        """

        self.session = None
        self.user = None
        self.room = None

        super().__init__(*args, **kwargs)

    ###############################################################################################
    # Connection Methods                                                                          #
    ###############################################################################################

    async def connect(self):
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

        # Set the session
        # TODO: Consider pros and cons filesystem/cache/cookie sessions vs database sessions
        self.session = self.scope["session"]

        # Set the user
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
        else:
            # Make an OBUser object for this anonymous user's session
            while try_get(OBUser, username=f"{ANON_PREFIX}{self.session.session_key}"):
                self.session.cycle_key()

            self.user = OBUser(username=f"{ANON_PREFIX}{self.session.session_key}")
            self.user.save()

        # Set the room
        room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room = await sync_get(Room, name=room_name)

        # Join room group
        await self.channel_layer.group_add(
            get_group_name(GroupTypes.Room, room_name),
            self.channel_name
        )

        # Add to the occupants list for this room
        room_object = await sync_get(Room, name=self.room.name)
        await sync_add(room_object.occupants, self.user)

        self.accept()

    async def disconnect(self, code):
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
        await self.channel_layer.group_discard(
            get_group_name(GroupTypes.Room, self.room.name),
            self.channel_name
        )

        print(f"WebSocket disconnected with code {code}.")

        # Remove from the occupants list for this room and remove the room reference
        await sync_remove(self.room.occupants, self.user)
        self.room = None

        # Delete anonymous users' temporary OBUser from the database and remove the user reference
        if not self.session.is_authenticated:
            await sync_delete(self.user)
            self.user = None

    ###############################################################################################
    # Messaging Methods                                                                           #
    ###############################################################################################

    async def receive(self, text_data=None, bytes_data=None):
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
        new_message_object = await sync_save(
            Message,
            message=message_text,
            sender=self.user,
            room=self.room
        )

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

    async def room_message(self, event):
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

        await self.send(text_data=event["message_json"])

    async def kick(self, event):
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
            await self.close()
