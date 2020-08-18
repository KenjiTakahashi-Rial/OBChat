"""
WhoCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import GroupTypes
from OB.models import Admin, Room
from OB.utilities.database import async_get_owner, async_len_all, async_model_list, async_try_get
from OB.utilities.event import send_system_room_message

class WhoCommand(BaseCommand):
    """
    Lists all the occupants in a room. Can be called without arguments to list the users of the
    issuing user's current room.
    """

    async def __init__(self, args, sender, room):
        """
        When there are no arguments, the default is the current room.
        """

        if not args:
            args = [room.name]

        super().__init__()

    async def check_arguments(self):
        """
        See BaseCommand.check_arguments().
        """

        for room_name in self.args:
            arg_room = await async_try_get(Room, group_type=GroupTypes.Room, name=room_name)

            if not arg_room:
                self.sender_receipt += [
                    f"{room_name} doesn't exist, so that probably means nobody is in there."
                ]
            else:
                self.valid_targets += [arg_room]

        return bool(self.valid_targets)

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
