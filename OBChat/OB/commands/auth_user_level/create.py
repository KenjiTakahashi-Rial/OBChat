"""
CreateCommand class container module
"""

from OB.commands.base import BaseCommand
from OB.constants import GroupTypes
from OB.models import Room
from OB.utilities.database import async_save, async_try_get
from OB.utilities.event import send_system_room_message

class CreateCommand(BaseCommand):
    """
    Create a new chat room from a commandline instead of through the website GUI.
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticated user
        if self.sender_privilege < Privilege.Admin:
            self.sender_receipt = ["Identify yourself! Must log in to create a room."]
        # Missing room name argument
        elif not args:
            self.sender_receipt = ["Usage: /create <name>"]
        # Too many arguments
        elif len(args) > 1:
            self.sender_receipt = ["Room name cannot contain spaces."]
        # Room with argument name already exists
        elif existing_room:
            self.sender_receipt = [f"Someone beat you to it. {existing_room} already exists."]

        return not self.sender_receipt


    # Check for errors
    if not args:
        error_message = "Usage: /create <name>"
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
        await send_system_room_message(error_message, room, [sender])
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
    await send_system_room_message(success_message, room, [sender])
