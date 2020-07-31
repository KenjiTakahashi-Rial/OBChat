"""
The BaseCommand class container module.
"""

from OB.constants import Privilege

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

        Arguments:
            args (list[string]): The arguments of the command. Some commands may not use arguments.
            sender (OBUser): The OBUser who issued the command.
            room (Room): The Room the command was sent from.
        """

        self.args = args
        self.sender = sender
        self.room = room
        self.error_messages = []
        self.sender_privilege = Privilege.Invalid

    async def execute(self):
        """
        This is where the main implementation of the command goes.
        """
