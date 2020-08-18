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

    async def check_initial_errors(self):
        """
        There are no initial errors for /who.
        """

        return True

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

    async def execute_implementation(self):
        """
        Construct a string of occupants in the room and send it back to the sender.
        The sender receipt includes per-argument error messages.
        """

        for room in self.valid_targets:
            occupants = await async_model_list(room)

            if not occupants:
                who_string = f"{room} is all empty!"
            else:
                who_string = f"Users in {room}:"

                for user in occupants:
                    user_suffix = ""

                    if user == await async_get_owner(room):
                        user_suffix += " [Owner]"
                    if await async_try_get(Admin, user=user, room=room):
                        user_suffix += " [Admin]"
                    if user == self.sender:
                        user_suffix += " [you]"

                    who_string += f"    {user}{user_suffix}\n"
