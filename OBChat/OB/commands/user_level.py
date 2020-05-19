"""
Any user may perform these commands.
"""

from OB.constants import GroupTypes
from OB.models import Admin, OBUser, Room
from OB.utilities.database import sync_get_owner, sync_len_all, sync_model_list, sync_save,\
    sync_try_get
from OB.utilities.event import send_private_message, send_system_room_message

async def who(args, sender, room):
    """
    Description:
        Lists all the occupants in a room. Can be called without arguments to list the users of the
        issuing user's current room.

    Arguments:
        args (list[string]): The names of the Rooms to list the occupants of. No argument implies
            the room parameter as the argument.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.

    Return values:
        None.
    """

    if not args:
        # Default to current room when no arguments
        args = [room.name]
    else:
        # Remove duplicates
        args = list(dict.fromkeys(args))

    error_messages = []
    who_strings = []

    for room_name in args:
        arg_room = await sync_try_get(Room, group_type=GroupTypes.Room, name=room_name)

        # Check for errors
        if not arg_room:
            error_messages += [f"{room_name} doesn't exist, so that probably means nobody is in "
                               "there."]
            continue
        elif await sync_len_all(arg_room.occupants) == 0:
            who_strings += [f"{room_name} is all empty!\n"]
            continue

        who_strings += [f"Users in {room_name}:"]
        who_string = ""

        for occupant in await sync_model_list(arg_room.occupants):
            occupant_string = "    " + str(occupant)

            # Tag occupant appropriately
            if occupant == await sync_get_owner(arg_room):
                occupant_string += " [owner]"
            if await sync_try_get(Admin, user=occupant, room=room):
                occupant_string += " [admin]"
            if occupant == sender:
                occupant_string += " [you]"

            who_string += occupant_string + "\n"

        if who_string:
            who_strings += [who_string]

    if who_strings:
        who_strings = ["\n"] + who_strings

    # Send user lists back to the sender
    await send_system_room_message("\n".join(error_messages + who_strings), room, sender)

async def private(args, sender, room):
    """
    Description:
        Sends a private message from the user parameter to another OBUser. The private message will
        have its own OBConsumer group where only the two users will receive messages.

    Arguments:
        args (list[string]): The first item should be a username prepended with '/' and the
            following strings should be words in the private message.
        sender (OBUser): Not used, but included as a parameter so the function can be called from
            the COMMANDS dict.
        room (Room): The Room the command was sent from.

    Return values:
        None.
    """

    error_message = ""

    # Check for initial errors
    if not args:
        error_message = "Usage: /private /<user> <message>"
    elif args[0][0] != '/':
        error_message = "Looks like you forgot a \"/\" before the username. I'll let it slide."
    else:
        recipient_object = await sync_try_get(OBUser, username=args[0][1:])
        # Check for per-argument errors
        if not recipient_object:
            error_message = (f"{args[0]} doesn't exist. Your private message will broadcasted "
                            "into space instead.")
        elif len(args) == 1:
            error_message = "No message specified. Did you give up at just the username?"

    # Send error message back to issuing user
    if error_message:
        await send_system_room_message(error_message, room, sender)
        return

    # Reconstruct message from args
    message_text = " ".join(args[1:])
    await send_private_message(message_text, sender, recipient_object)

async def create_room(args, sender, room):
    """
    Description:
        Create a new chat room from a commandline instead of through the website GUI.

    Arguments:
        args (list[string]): The desired name of the new room.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.

    Return values:
        None.
    """

    error_message = ""

    # Check for errors
    if not args:
        error_message = "Usage: /room <name>"
    elif not sender.is_authenticated or sender.is_anon:
        error_message = "Identify yourself! Must log in to create a room."
    elif len(args) > 1:
        error_message = "Room name cannot contain spaces."
    elif await sync_try_get(Room, group_type=GroupTypes.Room, name=args[0].lower()):
        error_message = f"Someone beat you to it. {args[0].lower()} already exists."

    # Send error message back to issuing user
    if error_message:
        await send_system_room_message(error_message, room, sender)
        return

    display_name = args[0] if not args[0].islower() else None

    # Save the new room
    created_room = await sync_save(
        Room,
        name=args[0].lower(),
        owner=sender,
        display_name=display_name
    )

    # Send success message back to issueing user
    success_message = f"Sold! Check out your new room: {created_room}"
    await send_system_room_message(success_message, room, sender)
