"""
A user must have admin privileges of the room to perform this command (see OB.models.Admin &
OB.constants.Privilege).
"""

from OB.constants import Privilege
from OB.models import Ban, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_try_get
from OB.utilities.event import send_system_room_message

async def elevate(args, sender, room):
    """
    Description:
        Requests an action (e.g. /kick, /ban, /lift) be performed by a user with higher privilege.
        Can request generally to all users with higher privilege or to a specific user.

    Arguments:
        args (list[string]): The command to elevate, the arguments of that command, and the user to
            elevate to (defaults to all users of higher privilege)
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # TODO: Implement this
