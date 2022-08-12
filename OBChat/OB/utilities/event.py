"""
Useful Consumer event functions.
"""

import json

from channels.layers import get_channel_layer

from OB.constants import GroupTypes
from OB.models import Message, OBUser, Room
from OB.strings import StringId
from OB.utilities.database import async_add, async_get, async_save, async_try_get
from OB.utilities.format import get_datetime_string, get_group_name


async def send_event(event, group_name):
    """
    Distributes an event to a consumer group.

    Arguments:
        event (dict): Contains the event type and variant event data. Each event type must have a
            corresponding handling method of the same name defined in the consumer class (see
            OB.consumers.OBConsumer).
        group_name (string): The name of the group to send the event to, as a string (see
            get_group_name()).
    """

    await get_channel_layer().group_send(group_name, event)


async def send_room_event(room_id, event):
    """
    Distributes an event to the consumer group associated with a room.

    Arguments:
        event (dict): Contains the event type and variant event data. Each event type must have
            a corresponding handling method of the same name defined in the consumer class, (see
            OBConsumer).
        room_id (int): The id of the room whose group to send the event to.
    """

    await send_event(event, get_group_name(GroupTypes.Room, room_id))


async def send_room_message(message_json, room_id, recipients=None, exclusions=None):
    """
    Sends an event of type "room_message", to a specified room (see OBConsumer.room_message()).
    This is the last operation performed for only the sender.

    Arguments:
        message_json (string): A JSON containing the message text and any metadata to be displayed.
        room_id (int): The id of the room to send the message to.
        recipients (list[OBUser] or None): The only users who will see the response. If None, all
            occupants of the room will see the response. If a user in this list is also in
            exclusions, they will not receive the message.
        exclusions (list[OBUser] or None): Users who will not see the response. If None, all
            recipients will see the response. If a user in this list is also in recipients, they
            will not receive the message.
    """

    event = {
        "type": "room_message",
        "message_json": message_json,
        "recipient_ids": [user.id for user in recipients] if recipients else [-1],
        "exclusion_ids": [user.id for user in exclusions] if exclusions else [-1],
    }

    await send_room_event(room_id, event)


async def send_system_room_message(message_text, room, recipients=None, exclusions=None):
    """
    Sends a message from the server to a specified room's group (see send_room_message()) with the
    server's OBUser database object as the sender.
    Saves the message in the database.

    Arguments:
        message_text (string): The message to send from the server.
        room (Room): The database object of the room to send this message to.
        recipients (list[OBUser] or None): The only users who will see the response. If None, all
            occupants of the room will see the response. If a user in this list is also in
            exclusions, they will not receive the message.
        exclusions (list[OBUser] or None): Users who will not see the response. If None, all
            recipients will see the response. If a user in this list is also in recipients, they
            will not receive the message.
    """

    if not message_text or message_text.isspace():
        return

    # Save message to database
    system_user = await async_get(OBUser, username=StringId.SystemUsername)
    new_message = await async_save(Message, message=message_text, sender=system_user, room=room)

    if recipients:
        for user in recipients:
            await async_add(new_message.recipients, user)
    else:
        await async_add(new_message.recipients, None)

    if exclusions:
        for user in exclusions:
            await async_add(new_message.exclusions, user)
    else:
        await async_add(new_message.exclusions, None)

    message_json = json.dumps(
        {
            "text": message_text,
            "sender_name": StringId.SystemUsername,
            "has_recipients": bool(recipients),
            "has_exclusions": bool(exclusions),
            "timestamp": get_datetime_string(new_message.timestamp),
        }
    )

    # Send the message
    await send_room_message(message_json, room.id, recipients, exclusions)


async def send_private_message(message_text, sender, recipient):
    """
    Sends a private message between two users.

    Arguments:
        message_text (string): The text of the message to send.
        sender (OBUser): The user sending the private message.
        recipient (OBUser): The user to send the private message to.
    """

    # Get the Room object for the private messages
    private_message_room = await async_try_get(Room, name=get_group_name(GroupTypes.Private, sender.id, recipient.id))

    # Create the database object if it doesn't exist
    if not private_message_room:
        private_message_room = await async_save(
            Room,
            group_type=GroupTypes.Private,
            name=get_group_name(GroupTypes.Private, sender.id, recipient.id),
        )

    # Save message to database
    new_message = await async_save(Message, message=message_text, sender=sender, room=private_message_room)

    # Encode the message data and metadata
    message_json = json.dumps(
        {
            "text": message_text,
            "sender_name": sender.display_name or sender.username,
            "timestamp": get_datetime_string(new_message.timestamp),
        }
    )

    # Send message to room group
    await send_room_message(message_json, private_message_room.id)
