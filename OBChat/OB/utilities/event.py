"""
Storage for event functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

import json
from channels.layers import get_channel_layer

from OB.constants import SYSTEM_USERNAME, GroupTypes
from OB.models import Message, OBUser, Room
from OB.utilities.database import sync_get, sync_save, sync_try_get
from OB.utilities.format import get_datetime_string, get_group_name

async def send_event(event, group_name):
    """
    Description:
        Distributes an event to a consumer group.

    Arguments:
        event (dict): Contains the event type and variant event data. Each event type must have a
            corresponding handling method of the same name defined in the consumer class (see
            OB.consumers.OBConsumer).
        group (string): The name of the group to send the event to, as a string (see
            get_group_name()).
    """

    await get_channel_layer().group_send(group_name, event)

async def send_room_event(room_id, event):
    """
    Description:
        Distributes an event to the consumer group associated with a room.

    Arguments:
        event (dict): Contains the event type and variant event data. Each event type must have
            a corresponding handling method of the same name defined in the consumer class, (see
            OBConsumer).
        room_id (int): The id of the room whose group to send the event to.
    """

    await send_event(event, get_group_name(GroupTypes.Room, room_id))

async def send_room_message(message_json, room_id, recipient=None):
    """
    Description:
        Sends an event of type "room_message", to a specified room (see OBConsumer.room_message()).
        This is the last operation performed for only the sender.

    Arguments:
        message_json (string): A JSON containing the message text and any metadata to be displayed.
        room_id (int): The id of the room to send the message to.
        recipient (OBUser): The only user who will see the response.
            If None, all occupants of the Room will see the response.
    """

    event = {
        "type": "room_message",
        "message_json": message_json,
        "recipient_id": -1 if not recipient else recipient.id
    }

    await send_room_event(room_id, event)

async def send_system_room_message(message_text, room, recipient=None):
    """
    Description:
        Sends a message from the server to a specified room's group (see send_room_message()) with
        the server's OBUser database object as the sender.
        Saves the message in the database.

    Arguments:
        message_text (string): The message to send from the server.
        room (Room): The database object of the room to send this message to.
        recipient (OBUser): The user who initiated the command and will see the response.
            If None, all occupants of the Room will see the response.
    """

    # Save message to database
    system_user_object = await sync_get(OBUser, username=SYSTEM_USERNAME)
    new_message_object = await sync_save(
        Message,
        message=message_text,
        sender=system_user_object,
        recipient=recipient,
        room=room
    )

    message_json = json.dumps({
        "text": message_text,
        "sender_name": SYSTEM_USERNAME,
        "has_recipient": bool(recipient),
        "timestamp": get_datetime_string(new_message_object.timestamp)
    })

    # Send the message
    await send_room_message(message_json, room.id, recipient)

async def send_private_message(message_text, sender, recipient):
    """
    Description:
        Sends a private message between two users. For user through OBLine.

    Arguments:
        sender (OBUser): The user sending the private message.
        recipient (OBUser): The user to send the private message to.
    """

    # Get the Room object for the private messages
    private_message_room = await sync_try_get(
        Room,
        name=get_group_name(GroupTypes.Private, sender.id, recipient.id)
    )

    # Create the database_object if it doesn't exist
    if not private_message_room:
        print("didn't exist")
        private_message_room = await sync_save(
            Room,
            group_type=GroupTypes.Private,
            name=get_group_name(GroupTypes.Private, sender.id, recipient.id)
        )


    # Save message to database
    new_message_object = await sync_save(
        Message,
        message=message_text,
        sender=sender,
        room=private_message_room
    )

    # Encode the message data and metadata
    message_json = json.dumps({
        "text": message_text,
        "sender_name": sender.display_name or sender.username,
        "timestamp": get_datetime_string(new_message_object.timestamp)
    })

    # Send message to room group
    await send_room_message(message_json, private_message_room.id)
