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
    """

    if not args:
        # Default to current room when no arguments
        args = [room.name]
    else:
        # Remove duplicates
        args = list(dict.fromkeys(args))

    return_strings = []

    for room_name in args:
        arg_room = await sync_try_get(Room, group_type=GroupTypes.Room, name=room_name)

        # Check for errors
        if not arg_room:
            return_strings += [f"{room_name} doesn't exist, so that probably means nobody is in "
                               "there."]
            continue

        if await sync_len_all(arg_room.occupants) == 0:
            return_strings += [f"{room_name} is all empty!"]
            continue

        return_strings += [f"Users in {room_name}:"]
        who_string = ""

        for occupant in await sync_model_list(arg_room.occupants):
            occupant_string = f"    {occupant}"

            # Tag occupant appropriately
            if occupant == await sync_get_owner(arg_room):
                occupant_string += " [owner]"
            if await sync_try_get(Admin, user=occupant, room=room):
                occupant_string += " [admin]"
            if occupant == sender:
                occupant_string += " [you]"

            who_string += occupant_string + "\n"

        if who_string:
            return_strings += [who_string]

    # Send user lists back to the sender
    await send_system_room_message("\n".join(return_strings), room, sender)

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
            error_message = (f"{args[0][1:]} doesn't exist. Your private message will broadcasted "
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
