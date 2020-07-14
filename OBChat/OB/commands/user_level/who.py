"""
Any user may perform this command.
"""

from OB.constants import GroupTypes
from OB.models import Admin, Room
from OB.utilities.database import async_get_owner, async_len_all, async_model_list, async_try_get
from OB.utilities.event import send_system_room_message

async def who(args, sender, room):
    """
    Description:
        Lists all the occupants in a room. Can be called without arguments to list the users of the
        issuing user's current room.

    Arguments:
        args (list[string]): The names of the Rooms to list the occupants of (defaults to the
            sender's current room).
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
        arg_room = await async_try_get(Room, group_type=GroupTypes.Room, name=room_name)

        # Check for errors
        if not arg_room:
            return_strings += [
                f"{room_name} doesn't exist, so that probably means nobody is in there."
            ]
            continue

        if await async_len_all(arg_room.occupants) == 0:
            return_strings += [f"{arg_room} is all empty!"]
            continue

        return_strings += [f"Users in {arg_room}:"]
        who_string = ""

        for occupant in await async_model_list(arg_room.occupants):
            occupant_string = f"    {occupant}"

            # Tag occupant appropriately
            if occupant == await async_get_owner(arg_room):
                occupant_string += " [Owner]"
            if await async_try_get(Admin, user=occupant, room=room):
                occupant_string += " [Admin]"
            if occupant == sender:
                occupant_string += " [you]"

            who_string += occupant_string + "\n"

        if who_string:
            return_strings += [who_string]

    # Send user lists back to the sender
    await send_system_room_message("\n".join(return_strings), room, [sender])
