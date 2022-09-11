"""
PrivateCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.models import OBUser
from OB.strings import StringId
from OB.utilities.database import async_try_get
from OB.utilities.event import send_private_message, send_system_room_message


class PrivateCommand(BaseCommand):
    """
    Sends a private message from the user parameter to another OBUser.
    The private message will have its own OBConsumer group where only the two users will receive
    messages.
    """

    CALLERS = [StringId.PrivateCaller, StringId.PrivateCallerShort]
    MANUAL: str = StringId.PrivateManual

    async def check_initial_errors(self) -> bool:
        """
        See BaseCommand.check_initial_errors().
        """

        # Missing target and message arguments
        if not self.args:
            self.sender_receipt = [StringId.PrivateSyntax]
        # Invalid syntax
        elif self.args[0][0] != "/":
            self.sender_receipt = [StringId.PrivateInvalidSyntax]

        return not self.sender_receipt

    async def check_arguments(self) -> bool:
        """
        See BaseCommand.check_arguments().
        """

        self.valid_targets = [await async_try_get(OBUser, username=self.args[0][1:])]

        if not self.valid_targets[0]:
            self.sender_receipt = [StringId.PrivateInvalidTarget.format(self.args[0][1:])]
        elif len(self.args) == 1:
            self.sender_receipt = [StringId.PrivateNoMessage]

        return bool(self.valid_targets)

    async def execute_implementation(self) -> None:
        """
        Reconstruct the original message from the command arugments.
        """

        self.targets_notification = [" ".join(self.args[1:])]

    async def send_responses(self) -> None:
        """
        For private messages, the only response should be errors or the private message, itself.
        Send the message to both the target and the user in its own private room.
        """

        if self.sender_receipt:
            await send_system_room_message("\n".join(self.sender_receipt), self.room, [self.sender])
        elif self.targets_notification:
            await send_private_message(self.targets_notification[0], self.sender, self.valid_targets[0])
