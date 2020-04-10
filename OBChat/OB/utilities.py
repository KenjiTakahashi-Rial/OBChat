from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .enums import GroupTypes
from .models import Message, OBUser

def get_system_user():
    return OBUser.objects.get(username="OB-Sys")

def get_group_name(group_type, name, second_name=""):
    switch = {
        GroupTypes.Invalid: name,
        GroupTypes.Line: f"{name}_OB-Sys",
        GroupTypes.Room: f"room_{name}",
        GroupTypes.Private: f"{min(name, second_name)}_{max(name, second_name)}"
    }

    return switch[group_type]

def send_room_message(message, sender, room):
    async_to_sync(get_channel_layer().group_send)(
        get_group_name(GroupTypes.Room, room.name),
        {
            "type": "room_message",
            "message": message
        }
    )

    # Save chat message to database
    if  message:
        Message(message=message, sender=sender, room=room).save()

def send_system_room_message(message, room):
    send_room_message(message, get_system_user(), room)

def send_private_message(message, sender, recipient):
    # TODO: Implement this
    pass

def send_system_operation(operation, user, group):
    async_to_sync(get_channel_layer().group_send)(
        group,
        {
            "type": "system_operation",
            "operation": operation,
            "user": user
        }
    )

def is_command(message):
    if len(message) > 1:
        return message[0] == "/" and message[1] != "/"

    return message and message[0] == "/"
