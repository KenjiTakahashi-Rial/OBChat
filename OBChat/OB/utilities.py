import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .constants import SYSTEM_USERNAME, GroupTypes, Privilege
from .models import Admin, Message, OBUser

def try_get(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def get_group_name(group_type, name, second_name=""):
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

def send_room_message(message_json, room):
    async_to_sync(get_channel_layer().group_send)(
        get_group_name(GroupTypes.Room, room.name),
        {
            "type": "room_message",
            "message_json": message_json
        }
    )

def send_system_room_message(message_text, room):
    # Save message to database
    system_user = OBUser.objects.get(username=SYSTEM_USERNAME)
    message = Message(message=message_text, sender=system_user, room=room)
    message.save()

    message_json = json.dumps({
        "text": message_text,
        "sender": SYSTEM_USERNAME,
        "timestamp": message.timestamp
    })

    send_room_message(message_json, room)

def send_private_message(message):
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

def is_admin(username, room):

    if username == room.owner.username:
        return Privilege.Owner

    admin_query = try_get(Admin, username=username)

    if admin_query:
        if admin_query.is_unlimited:
            return Privilege.UnlimitedAdmin

        return Privilege.Admin

    return Privilege.User
