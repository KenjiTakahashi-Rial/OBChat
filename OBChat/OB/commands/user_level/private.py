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
        elif args[0][0] != '/':
            self.sender_receipt = ["Looks like you forgot a \"/\" before the username. I'll let it slide."]


        # Check for per-argument errors
        recipient = await async_try_get(OBUser, username=args[0][1:])
        if not recipient:
            error_message = (
                f"{args[0][1:]} doesn't exist. Your private message will broadcasted into space "
                "instead."
            )
        elif len(args) == 1:
            error_message = "No message specified. Did you give up at just the username?"

        # Send error message back to issuing user
        if error_message:
            await send_system_room_message(error_message, room, [sender])
            return

        # Reconstruct message from args
        message_text = " ".join(args[1:])
        await send_private_message(message_text, sender, recipient)
