from OB.enums import GroupTypes
from OB.utilities import send_chat_message

def delete_room(args, user, room_name):
    """
    Description:
        Delete a room
        Must have ownership
    Arguments:
        A Server object
        A list of arguments
        The client object that issued the command
    Return Value:
        True if the command was carried out
        False if an error occurred
    """

    if len(args) > 1:
        send_chat_message("Room name cannot contain spaces", client)

        return False

    if len(args) == 0:
        args.append(client.room.name)

    if args[0] not in self.rooms:
        send_chat_message(f"Room does not exist: {args[0]}", client)

        return False

    if client.username != self.rooms[args[0]].owner:
        send_chat_message(f"Insufficient privileges to delete: {args[0]}", client)

        return False

    # Get the room object
    room = self.rooms[args[0]]

    for user in room.users:
        user.room = None
        user.typing = ""

        if user.username != room.owner:
            send_chat_message(f"The room was deleted: {room.name}", user)

    del self.rooms[args[0]]

    send_chat_message(f"Deleted room: {args[0]}", client)

    return True