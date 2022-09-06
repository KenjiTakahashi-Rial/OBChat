"""
The BaseCommand class container module.
"""

from OB.constants import Privilege
from OB.utilities.command import async_get_privilege
from OB.utilities.event import send_system_room_message


class BaseCommand:
    """
    A superclass for all commands.
    Allow commands to be carried out generically by OB.commands.command_handler.
    """

    # The different ways the command can be called
    CALLERS = []
    # The message describing how to use the command
    # TODO: Change these to use string IDs instead
    MANUAL = ""

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

        # Responses to send after processing the command
        self.sender_receipt = []
        self.occupants_notification = []
        self.targets_notification = []

        # Valid targets for the command, type varying by command
        self.valid_targets = []

        self.remove_duplicates = True

    async def execute(self):
        """
        This is the driver code behind the command.
        """

        if self.remove_duplicates:
            self.args = list(dict.fromkeys(self.args))

        # Get the sender's privilege
        self.sender_privilege = await async_get_privilege(self.sender, self.room)

        # Check for initial errors
        if not await self.check_initial_errors():
            pass
        # Check the validity of the arguments
        elif not await self.check_arguments():
            pass
        # Execute the command
        else:
            await self.execute_implementation()

        await self.send_responses()

    async def check_initial_errors(self):
        """
        Check for initial errors such as lack of privilege or invalid syntax.
        Save initial error messages in the sender receipt instance variable.

        Return values:
            boolean: True if there were no initial errors.
        """

    async def check_arguments(self):
        """
        Check each argument for errors such as self-targeting or targeting a user of higher
        privilege.
        Save per-argument error messages in the sender_receipt instance variable.
        Save the valid arguments in the valid_targets instance variable.

        Return values:
            boolean: True if any of the arguments are a valid ban.
        """

    async def execute_implementation(self):
        """
        The main implementation of the command function.
        """

    async def send_responses(self):
        """
        Sends the sender a receipt of errors and successes.
        Sends other occupants of the room a notification of a command's execution.
        Joins the sender receipt and occupants notification lists by \n.
        """

        await send_system_room_message("\n".join(self.sender_receipt), self.room, [self.sender])

        await send_system_room_message(
            "\n".join(self.occupants_notification),
            self.room,
            exclusions=[self.sender] + self.valid_targets,
        )

        await send_system_room_message("\n".join(self.targets_notification), self.room, self.valid_targets)
