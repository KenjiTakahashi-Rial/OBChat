"""
Any user may perform these commands.
"""

from OB.models import Admin, Room, OBUser
from OB.utilities.database import sync_get_who_string, sync_len_all, sync_try_get
from OB.utilities.event import send_private_message, send_system_room_message

async def who(args, user, room):
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

    # Check for inital errors
    error_message = ""

    if len(args) > 1:
        error_message = "Room name cannot contain spaces."
    else:
        args.append(room.name)

    who_strings = []

    for room_name in args:
        arg_room = await sync_try_get(Room, name=room_name)

        # Check for per-argument errors
        if not arg_room:
            error_message = f"{args[0]} doesn't exist, so that probably means nobody is in \
                there."
        else:
            if await sync_len_all(room.occupants) == 0:
                error_message = f"{args[0]} is all empty!"

        # Send error message back to issuing user
        if error_message:
            await send_system_room_message(error_message, room)
            return

        who_strings.append(await sync_get_who_string(user, arg_room))

    # Send user list back to the issuing user
    await send_system_room_message("\n\n".join(who_strings), room)

async def private(args, user, room):
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

    # Check for initial errors
    if not args:
        error_message = "Usage: /private /<user> <message>"
    elif args[0][0] != '/':
        error_message = "Looks like you forgot a \"/\" before the username. I'll let it slide."
    else:
        recipient_object = await sync_try_get(OBUser, username=args[0][1:])

    # Check for per-argument errors
    if not recipient_object:
        error_message = f"\"{args[0]}\" doesn't exist. Your private message will broadcasted \
            into space instead."
    elif len(args) == 1:
        error_message = "No message specified. Did you give up at just the username?"

    # Send error message back to issuing user
    if error_message:
        await send_system_room_message(error_message, room)
        return

    # Reconstruct message from args
    message_text = " ".join(args[1:])

    await send_private_message()

async def create_room(args, user, room):
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

    # Check for errors
    if not args:
        error_message = "Usage: /room <name>"
    elif not user.is_authenticated:
        error_message = "Identify yourself! Must log in to create a room."
    elif len(args) > 1:
        error_message = "Room name cannot contain spaces."
    elif Room.objects.filter(name=args).exists():
        error_message = f"Someone beat you to it. \"{args[0]}\" already exists."

    # Send error message back to issuing user
    if error_message:
        await send_system_room_message(error_message, room)
        return

    # Save the new room
    new_room_object = Room(name=args, owner=user)
    new_room_object.save()

    # Send success message back to issueing user
    success_message = f"Sold! Check out your new room: \"{args[0]}\""
    await send_system_room_message(success_message, room)
