"""
WhoCommand class container module.
"""

from typing import Any, Optional

from OB.commands.base import BaseCommand
from OB.constants import GroupTypes
from OB.models import Admin, Room, OBUser
from OB.strings import StringId
from OB.utilities.database import async_get_owner, async_model_list, async_try_get


class WhoCommand(BaseCommand):
    """
    Lists all the occupants in a room. Can be called without arguments to list the users of the
    issuing user's current room.
    """

    CALLERS: tuple[str, ...] = (StringId.WhoCaller, StringId.WhoCallerShort)
    MANUAL: str = StringId.WhoManual

    def __init__(self, args: list[str], sender: OBUser, room: Room):
        """
        When there are no arguments, the default is the current room.
        """

        if not args:
            args = [room.name]

        super().__init__(args, sender, room)

    async def check_initial_errors(self) -> bool:
        """
        There are no initial errors for /who.
        """

        return True

    async def check_arguments(self) -> bool:
        """
        See BaseCommand.check_arguments().
        """

        for room_name in self.args:
            arg_room: Optional[Room] = await async_try_get(Room, group_type=GroupTypes.Room, name=room_name)

            if not arg_room:
                self.sender_receipt += [StringId.WhoInvalidTarget.format(room_name)]
            else:
                self.valid_targets += [arg_room]

        return bool(self.valid_targets)

    async def execute_implementation(self) -> None:
        """
        Construct a string of occupants in the room and send it back to the sender.
        The sender receipt includes per-argument error messages.
        """

        for room in self.valid_targets:
            # Revisit this "Any"
            occupants: list[Any] = await async_model_list(room.occupants)
            who_string: str

            if not occupants:
                who_string = StringId.WhoEmpty.format(room)
            else:
                who_string = StringId.WhoPreface.format(room) + "\n"

                for user in occupants:
                    user_suffix = ""

                    if user == await async_get_owner(room):
                        user_suffix += StringId.OwnerSuffix
                    if await async_try_get(Admin, user=user, room=room):
                        user_suffix += StringId.AdminSuffix
                    if user == self.sender:
                        user_suffix += StringId.YouSuffix

                    who_string += f"    {user}{user_suffix}\n"

            self.sender_receipt += [who_string]
