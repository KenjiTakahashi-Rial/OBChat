"""
Any user may perform this command.
"""

from OB.models import OBUser
from OB.utilities.database import async_try_get
from OB.utilities.event import send_private_message, send_system_room_message

async def private(args, sender, room):
    """
    Description:
        Sends a private message from the user parameter to another OBUser. The private message will
        have its own OBConsumer group where only the two users will receive messages.

    Arguments:
        args (list[string]): The first item should be a username prepended with '/' and the
            following strings should be words in the private message.
        sender (OBUser): Not used, but included as a parameter so the function can be called from
            the COMMANDS dict.
        room (Room): The Room the command was sent from.
    """

    error_message = ""

    # Check for initial errors
    if not args:
        error_message = "Usage: /private /<user> <message>"
    elif args[0][0] != '/':
        error_message = "Looks like you forgot a \"/\" before the username. I'll let it slide."
    else:
        recipient = await async_try_get(OBUser, username=args[0][1:])
        # Check for per-argument errors
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
