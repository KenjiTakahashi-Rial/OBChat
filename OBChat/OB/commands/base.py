"""
The BaseCommand class container module.
"""

class BaseCommand:
    """
    A superclass for all commands.
    Allows commands to be carried out generically by OB.commands.command_handler.
    """
    def __init__(self, command_string, sender, room):
        """
        Declares the instance variables that will be used for the command execution.

        Arguments:
            args (list[string]): The arguments of the command. Some commands may not use arguments.
            sender (OBUser): The OBUser who issued the command.
            room (Room): The Room the command was sent from.
        """

        self.command_string = command_string
        self.sender = sender
        self.room = room

    async def parse(self):
        """
        This is where the command string is parsed into arguments.
        """

    async def execute(self):
        """
        This is where the main implementation of the command goes.
        """
