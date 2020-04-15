from OB.models import Admin, Room, OBUser
from OB.utilities import send_private_message, send_system_room_message, try_get

def who(args, user, room):
    """
    Description:
        Lists all the occupants in a room. Can be called without arguments to list the users of the
        issuing user's current room.

    Arguments:
        args (list[string]): The name of the Room to list to occupants of. Should have length 0 or
            1, where 0 implies the room parameter as the argument.
        user (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was issued in.

    Return values:
        None
    """

    if not args and room is None:
        error_message = "You're not in a room."
    elif len(args) > 1:
        error_message = "Room name cannot contain spaces."
    else:
        args.append(room.name)

    if not Room.objects.filter(name=args[0]).exists():
        error_message = f"\"{args[0]}\" doesn't exist, so that probably means nobody is in there."
    else:
        if len(room.occupants.all()) == 0:
            error_message = f"\"{args[0]}\" is all empty!"

    if error_message:
        send_system_room_message(error_message, room)
        return

    # Iterate through users in room
    user_list_string = f"Chatters in: \"{args[0]}\" ({room.name})\n"

    for occupant in room.occupants.all():
        who_user = occupant.username

        # Tag user appropriately
        if occupant == room.owner:
            user_list_string += " (owner)"

        if Admin.objects.filter(user=user, room=room).exists():
            user_list_string += " (admin)"

        if occupant == user:
            user_list_string += " (you)"

        user_list_string += f"\n * {who_user}\nEnd list"

    send_system_room_message(user_list_string, room)

def private(args, user, room):
    """
    Description:
        Sends a private message from the user parameter to another OBUser. The private message will
        have its own OBConsumer group where only the two users will receive messages.

    Arguments:
        args (list[string]): The first item should be a username prepended with '/' and the
            following strings should be words in the private message.
        user (OBUser): Not used, but included as a parameter so the function can be called from the
            COMMANDS dict.
        room (Room): The room the command was issued in.

    Return values:
        None
    """

    if not args:
        error_message = "Usage: /private /<user> <message>"
    elif args[0][0] != '/':
        error_message = "Looks like you forgot a \"/\" before the username. I'll let it slide."
    else:
        recipient_object = try_get(OBUser, username=args[0][1:])

    if not recipient_object:
        error_message = f"\"{args[0]}\" doesn't exist. Your private message will broadcasted \
            into space instead."
    elif len(args) == 1:
        error_message = "No message specified. Did you give up halfway through?"

    if error_message:
        send_system_room_message(error_message, room)
        return

    # Reconstruct message from args
    message_text = " ".join(args[1:])

    # TODO: Once the function is filled in, put the appropriate arguments
    send_private_message()

def create_room(args, user, room):
    """
    Description:
        Create a new chat room from a commandline instead of through the website GUI.

    Arguments:
        args (list[string]): The desired name of the new room. Should have length 1.
        user (OBUser): The OBUser who issued the command call and the owner of the new room.
        room (Room): The room the command was issued in.

    Return values:
        None
    """

    if not args:
        return_message = "Usage: /room <name>"
    elif not user.is_authenticated:
        return_message = "Identify yourself! Must log in to create a room."
    elif len(args) > 1:
        return_message = "Room name cannot contain spaces."
    elif Room.objects.filter(name=args).exists():
        return_message = f"Someone beat you to it. \"{args[0]}\" already exists."
    else:
        new_room_object = Room(name=args, owner=user)
        new_room_object.save()
        return_message = f"Sold! Check out your new room: \"{args[0]}\""

    send_system_room_message(return_message, room)
