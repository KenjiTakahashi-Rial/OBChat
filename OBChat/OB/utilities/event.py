"""
Storage for event functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from OB.constants import SYSTEM_USERNAME, GroupTypes
from OB.models import Message, OBUser

def get_group_name(group_type, name, second_name=""):
    """
    Description:
        Get the correctly formatted name of a group as a string.

    Arguments:
        group_type (GroupType): The type of the desired group name.
        name (string): The name of the target room or user of this group
        second_name (string): The name of the second target user. For private messages.

    Return values:
        A formatted group name string, if the GroupType was valid.
        Otherwise the name parameter's argument.
    """

    switch = {
        GroupTypes.Invalid:
            name,
        GroupTypes.Line:
            f"{name}_OB-Sys",
        GroupTypes.Room:
            f"room_{name}",
        GroupTypes.Private:
            f"{min(name, second_name)}_{max(name, second_name)}"
    }

    return switch[group_type]

def send_event(event, group_name):
    """
    Description:
        Distributes an event to a consumer group.

    Arguments:
        event (dict): Contains the event type and variant event data. Each event type must have a
            corresponding handling method of the same name defined in the consumer class (see 
            OBConsumer).
        group (string): The name of the group to send the event to, as a string (see
            get_group_name()).

    Return values:
        None
    """

    # TODO: Consider making this asyncronous
    async_to_sync(get_channel_layer().group_send)(group_name, event)

def send_room_event(room_name, event):
    """
    Description:
        Distributes an event to the consumer group associated with a room.

    Arguments:
        event (dict): Contains the event type and variant event data. Each event type must have
            a corresponding handling method of the same name defined in the consumer class, (see
            OBConsumer).
        room_name (string): The name of the room whose group to send the event to.

    Return values:
        None
    """

    send_event(event, get_group_name(GroupTypes.Room, room_name))

def send_room_message(message_json, room_name):
    """
    Description:
        Send an event of type "room_message", to a specified room (see OBConsumer.room_message()).
        This is the last operation performed for only the sender.

    Arguments:
        message_json (string): A JSON containing the message text and any metadata to be displayed.
        room (Room): The database object of the room to send this message to.

    Return values:
        None
    """

    event = {
        "type": "room_message",
        "message_json": message_json
    }

    send_room_event(room_name, event)

def send_system_room_message(message_text, room):
    """
    Description:
        Send a message from the server to a specified room's group (see send_room_message()) with
        the server's OBUser database object as the sender.
        Saves the message in the database.

    Arguments:
        message_text (string): The message to send from the server.
        room (Room): The database object of the room to send this message to.

    Return values:
        None
    """

    # Save message to database
    system_user_object = OBUser.objects.get(username=SYSTEM_USERNAME)
    new_message_object = Message(message=message_text, sender=system_user_object, room=room)
    new_message_object.save()

    message_json = json.dumps({
        "text": message_text,
        "sender": SYSTEM_USERNAME,
        "timestamp": new_message_object.timestamp
    })

    # Send the message
    send_room_message(message_json, room.name)

def send_private_message():
    """
    Description:
        ...

    Arguments:
        ...

    Return values:
        ...
    """
    # TODO: Implement this
