"""
PrivateCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.models import OBUser
from OB.utilities.database import async_try_get
from OB.utilities.event import send_private_message, send_system_room_message

class PrivateCommand(BaseCommand):
    """
    Sends a private message from the user parameter to another OBUser.
    The private message will have its own OBConsumer group where only the two users will receive
    messages.
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Missing target and message arguments
        if not self.args:
            self.sender_receipt = ["Usage: /private /<user> <message>"]
        # Invalid syntax
        elif self.args[0][0] != '/':
            self.sender_receipt = [
                "Looks like you forgot a \"/\" before the username. I'll let it slide."
            ]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_arguments().
        """

        self.valid_targets = [await async_try_get(OBUser, username=self.args[0][1:])]

        if not self.valid_targets:
            self.sender_receipt = [
                f"{self.args[0][1:]} doesn't exist. Your private message will broadcasted into "
                "space instead."
            ]
        elif len(self.args) == 1:
            self.sender_receipt = ["No message specified. Did you give up at just the username?"]

        return bool(self.valid_targets)

    async def execute_implementation(self):
        """
        Reconstruct the original message from the command arugments.
        """

        self.targets_notification = [" ".join(self.args[1:])]

    async def send_responses(self):
        """
        For private messages, the only response should be errors or the private message, itself.
        Send the message to both the target and the user in its own private room.
        """

        if self.sender_receipt:
            await send_system_room_message(
                "\n".join(self.sender_receipt),
                self.room,
                [self.sender]
            )
        elif self.targets_notification:
            await send_private_message(
                self.targets_notification[0],
                self.sender,
                self.valid_targets[0]
            )
