"""
DeleteCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, Ban, Message
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_model_list, async_filter
from OB.utilities.event import send_room_event, send_system_room_message

class DeleteCommand(BaseCommand):
    """
    Deletes an existing Room database object.
    All Admin, Ban, and Message objects will be deleted as well.
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is not the owner
        if self.sender_privilege < Privilege.Owner:
            error_message = (
                "Trying to delete someone else's room? How rude. Only the room owner may delete a "
                "room"
            )
