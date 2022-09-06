"""
DeleteCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, Ban, Message
from OB.strings import StringId
from OB.utilities.database import (
    async_delete,
    async_model_list,
    async_filter,
    async_get_owner,
)
from OB.utilities.event import send_room_event


class DeleteCommand(BaseCommand):
    """
    Deletes an existing Room database object.
    All Admin, Ban, and Message objects will be deleted as well.
    """

    CALLERS = ["delete", "d"]
    MANUAL = f"/{CALLERS[0]} <room1> <room2> ... - Delete a room. Default: current room"

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is not the owner
        if self.sender_privilege < Privilege.Owner:
            self.sender_receipt = [StringId.NonOwnerDeleting]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_arguments().
        """

        # Missing or invalid target arguments
        if (
            len(self.args) != 2
            or self.args[0] != self.room.name
            or self.args[1] != (await async_get_owner(self.room)).username
        ):
            self.sender_receipt = [StringId.DeleteSyntax]

        return not self.sender_receipt

    async def execute_implementation(self):
        """
        Kicks users, deletes Admins, deletes Bans, deletes Messages, and finally deletes the Room.
        """

        # Kick all users
        for user in await async_model_list(self.room.occupants):
            kick_event = {"type": "kick", "target_id": user.id}
            await send_room_event(self.room.id, kick_event)

        # Delete all Admins
        for admin in await async_filter(Admin, room=self.room):
            await async_delete(admin)

        # Delete all Bans
        for ban in await async_filter(Ban, room=self.room):
            await async_delete(ban)

        # Delete all Messages
        for message in await async_filter(Message, room=self.room):
            await async_delete(message)

        # Delete the room
        await async_delete(self.room)
