"""
CreateCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import GroupTypes, Privilege
from OB.models import Room
from OB.utilities.database import async_save, async_try_get

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
        elif not self.args:
            self.sender_receipt = ["Usage: /create <name>"]
        # Too many arguments
        elif len(self.args) > 1:
            self.sender_receipt = ["Room name cannot contain spaces."]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_initial_errors()
        """

        existing_room = await async_try_get(
            Room,
            group_type=GroupTypes.Room,
            name=self.args[0].lower()
        )

        # Room with argument name already exists
        if existing_room:
            self.sender_receipt += [f"Someone beat you to it. {existing_room} already exists."]
            return False

        return True

    async def execute_implementation(self):
        """
        Create the new room with the sender of the command as the owner.
        Construct a string to send back to the sender.
        """

        # If there are capitalized letters in the argument room name, set the argument room name
        # as the display name and the lowecase version of it as the room name
        display_name = self.args[0] if not self.args[0].islower() else None

        # Save the new room
        created_room = await async_save(
            Room,
            name=self.args[0].lower(),
            owner=self.sender,
            display_name=display_name
        )

        self.sender_receipt += [f"Sold! Check out your new room: {created_room}"]
