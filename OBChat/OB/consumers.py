"""
Consumers manage OBChat's WebSocket communication.

See the Django Channels documentation on Consumers for more information.
https://channels.readthedocs.io/en/latest/topics/consumers.html
"""

import json

from channels.generic.websocket import AsyncWebsocketConsumer

from OB.commands.command_handler import handle_command
from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import Ban, Message, OBUser, Room
from OB.utilities.command import is_command
from OB.utilities.database import async_add, async_delete, async_get, async_remove, async_save,\
    async_try_get, async_model_list
from OB.utilities.event import send_room_message
from OB.utilities.format import get_datetime_string, get_group_name
from OB.utilities.session import async_cycle_key

class OBConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        """
        Description:
            Defines the instance variables for this consumer's session, user, and room.
            The session and user are unique to each OBConsumer.
            The room is not unique.
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
        """

        # Set the session
        # TODO: Consider pros and cons filesystem/cache/cookie sessions vs database sessions
        self.session = self.scope["session"]
        if not self.session.session_key:
            await async_cycle_key(self.session)

        # Set the user
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
        else:
            # Make an OBUser object for this anonymous user's session
            while await async_try_get(OBUser, username=f"{ANON_PREFIX}{self.session.session_key}"):
                await async_cycle_key(self.session)

            self.user = await async_save(
                OBUser,
                username=f"{ANON_PREFIX}{self.session.session_key}",
                is_anon=True
            )

        # Chat room
        if "room_name" in self.scope["url_route"]["kwargs"]:
            room_name = self.scope["url_route"]["kwargs"]["room_name"]
            group_type = GroupTypes.Room
        # Private message
        elif "username" in self.scope["url_route"]["kwargs"]:
            target_username = self.scope["url_route"]["kwargs"]["username"]
            target_user = await async_get(OBUser, username=target_username)
            room_name = get_group_name(GroupTypes.Private, self.user.id, target_user.id)
            group_type = GroupTypes.Private
        else:
            raise SystemError("OBConsumer could not get arguments from URL route.")

        self.room = await async_get(Room, group_type=group_type, name=room_name)

        # Stop here if banned
        if await async_try_get(Ban, user=self.user, room=self.room):
            return

        # Add to room group
        await self.channel_layer.group_add(
            get_group_name(GroupTypes.Room, self.room.id),
            self.channel_name
        )

        # Add to the occupants list for this room
        room = await async_get(Room, group_type=group_type, name=room_name)
        await async_add(room.occupants, self.user)

        await self.accept()

    async def disconnect(self, code):
        """
        Description:
            Leaves the Room group that this consumer was a part of. It will no longer send to or
            receive from that group.
            Remove the OBConsumer's user reference to the OBConsumer's room reference's list of
            occupants.
            Called automatically when a WebSocket connection is disconnected by the client.

        Arguments:
            code: A disconnect code to indicate disconnect conditions
        """

        # Leave room group
        await self.channel_layer.group_discard(
            get_group_name(GroupTypes.Room, self.room.id),
            self.channel_name
        )

        print(f"WebSocket disconnected with code {code}.")

        if code == "safe":
            return

        # Remove from the occupants list for this room and remove the room reference
        await async_remove(self.room.occupants, self.user)
        self.room = None

        # Delete anonymous users' temporary OBUser from the database and remove the user reference
        if self.user.is_anon:
            await async_delete(self.user)
            self.user = None

    async def close(self, code=None):
        """
        Description:
            Forcibly closes a WebSocket from the server.

        Arguments:
            code: A close code to indicate close conditions
        """

        await self.disconnect(code)
        await super().close(code)

    ###############################################################################################
    # Messaging Methods                                                                           #
    ###############################################################################################

    async def receive(self, text_data=None, bytes_data=None):
        """
        Description:
            Received a decoded WebSocket frame from the client, NOT from another consumer in this
            consumers group.
            Only the consumer whose user sent the message will call this method.
            This is called first in the consumer messaging process.
            Finally, if the message is a command, then handle it (see is_command()).

        Arguments:
            text_data (string): A JSON string containing the message text. Constructed in the
                JavaScript of room.html.
            bytes_data: Not used yet, but will contain images or other message contents which
                cannot be represented by text.
        """

        # Skip empty messages
        if not text_data and not bytes_data:
            return

        # Decode the JSON
        message_text = json.loads(text_data)["message_text"]

        # Save message to database
        new_message = await async_save(
            Message,
            message=message_text,
            sender=self.user if not self.user.is_anon else None,
            room=self.room,
            anon_username=self.user.username if self.user.is_anon else None
        )

        # Add sender as the only recipient if message is a command
        await async_add(new_message.recipients, self.user if is_command(message_text) else None))
        recipients = await async_model_list(new_message.recipients)

        # Encode the message data and metadata
        message_json = json.dumps({
            "text": message_text,
            "sender_name": self.user.display_name or self.user.username,
            "has_recipient": bool(recipients),
            "timestamp": get_datetime_string(new_message.timestamp)
        })

        # Send message to room group
        await send_room_message(message_json, self.room.id, recipients)

        if is_command(message_text):
            # Handle command
            await handle_command(message_text, self.user, self.room)

    # This may be of use later on
    async def send(self, text_data=None, bytes_data=None, close=False):
        """
        Description:
            Send an encoded WebSocket frame to the client, NOT to another consumer in this
            consumers group.
            Each consumer of a group which receives a message event will call this method.
            This is called last in the consumer messaging process.

        Arguments:
            text_data (string): A JSON string containing the message text.
            bytes_data: Not used yet, but will contain images or other message contents which
                cannot be represented by text.
            close: Used to send a WebSocket close signal to terminate the connection.
        """

        await super().send(text_data, bytes_data, close)

    ###############################################################################################
    # Event Handler Methods                                                                       #
    ###############################################################################################

    async def room_message(self, event):
        """
        Description:
            An event of type "room_message" was sent to a group this consumer is a part of.
            Send the message JSON to the client associated with this consumer.

        Arguments:
            event (dict): Contains the message JSON
        """

        if not event["recipients"] or self.user in event["recipients"]:
            await self.send(text_data=event["message_json"])

    async def kick(self, event):
        """
        Description:
            An event of type "kick" was sent to a group this consumer is a part of.
            Perform actions depending on if the user associated with this consumer is specified.

        Arguments:
            event (dict): Contains the target user's ID
        """

        if event["target_id"] == self.user.id:
            refresh_signal = {"refresh": True}
            await self.send(text_data=json.dumps(refresh_signal))
            await self.close("kick")
