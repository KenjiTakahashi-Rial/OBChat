from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .enums import GroupTypes

def get_group_name(group_type, name, second_name=""):
    switch = {
        GroupTypes.Invalid: name,
        GroupTypes.Line: f"OBLine_{name}",
        GroupTypes.Room: f"room_{name}",
        GroupTypes.Private: f"{min(name, second_name)}_{max(name, second_name)}"
    }

    return switch[group_type]

def send_chat_message(message, group):
    async_to_sync(get_channel_layer().group_send)(
        group,
        {
            "type": "chat_message",
            "message": message
        }
    )

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
    else:
        return message and message[0] == "/"
