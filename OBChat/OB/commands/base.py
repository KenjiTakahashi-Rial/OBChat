"""
The BaseCommand class container module.
"""

from OB.constants import Privilege
from OB.utilities.event import send_system_room_message

# pylint: disable=too-few-public-methods
# Justification: The only method that needs to be publicly visible is execute()
class BaseCommand:
    """
    A superclass for all commands.
    Allows commands to be carried out generically by OB.commands.command_handler.
    """

    def __init__(self, args, sender, room):
        """
        Declares the instance variables that will be used for the command execution.
        The sender receipt and occupants notification are lists of strings that are joined later.

        Arguments:
            args (list[string]): The arguments of the command. Some commands may not use arguments.
            sender (OBUser): The OBUser who issued the command.
            room (Room): The Room the command was sent from.
        """

        self.args = args
        self.sender = sender
        self.room = room
        self.sender_privilege = Privilege.Invalid
        self.sender_receipt = []
        self.occupants_notification = []

    async def execute(self):
        """
        This is where the main implementation of the command goes.
        """

    async def send_responses(self):
        """
        Sends the sender a receipt of errors and successes.
        Sends other occupants of the room a notification of a command's execution.
        Joins the sender receipt and occupants notification lists by \n.
        """

        await send_system_room_message(
            "\n".join(self.sender_receipt),
            self.room,
            [self.sender]
        )

        await send_system_room_message(
            "\n".join(self.occupants_notification),
            self.room,
            exclusions=[self.sender]
        )
