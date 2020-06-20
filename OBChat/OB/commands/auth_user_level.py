"""
A user must have be authenticated to perform these commands (see OB.models.Admin &
OB.utilities.command.get_privilege()).
"""

from OB.constants import GroupTypes
from OB.models import Room
from OB.utilities.database import async_save, async_try_get
from OB.utilities.event import send_system_room_message

async def create_room(args, sender, room):
    """
    Description:
        Create a new chat room from a commandline instead of through the website GUI.

    Arguments:
        args (list[string]): The desired name of the new room.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    error_message = ""

    # Check for errors
    if not args:
        error_message = "Usage: /room <name>"
    else:
        existing_room = await async_try_get(
            Room,
            group_type=GroupTypes.Room,
            name=args[0].lower()
        )

        if not sender.is_authenticated or sender.is_anon:
            error_message = "Identify yourself! Must log in to create a room."
        elif len(args) > 1:
            error_message = "Room name cannot contain spaces."
        elif existing_room:
            error_message = f"Someone beat you to it. {existing_room} already exists."

    # Send error message back to issuing user
    if error_message:
        await send_system_room_message(error_message, room, sender)
        return

    display_name = args[0] if not args[0].islower() else None

    # Save the new room
    created_room = await async_save(
        Room,
        name=args[0].lower(),
        owner=sender,
        display_name=display_name
    )

    # Send success message back to issueing user
    success_message = f"Sold! Check out your new room: {created_room}"
    await send_system_room_message(success_message, room, sender)

async def apply(args, sender, room):
    """
    Description:
        ...

    Arguments:
        args (list[string]): The desired name of the new room.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # TODO: Implement this
