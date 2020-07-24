"""
apply function container module
"""

from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_filter, async_get
from OB.utilities.event import send_system_room_message

async def apply(args, sender, room):
    """
    Sends a request for a user to be hired as an Admin or promoted to Unlimited Admin.
    The request is visible by all users with hiring privileges of the room.
    Optionally includes a message.

    Arguments:
        args (list[string]): An optional message to the users with hiring privileges.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    error_message = ""
    sender_privilege = await async_get_privilege(sender, room)

    # Check for errors
    if not sender.is_authenticated or sender.is_anon:
        error_message = (
            "You can't get hired looking like that! Clean yourself up and make an account first."
        )
    elif sender_privilege >= Privilege.UnlimitedAdmin:
        error_message = "You're already a big shot! There's nothing left to apply to."

    # Send error message back to issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    # Construct the application and receipt
    user_suffix = " [Admin]" if sender_privilege == Privilege.Admin else ""
    position_prefix = "Unlimited " if sender_privilege == Privilege.Admin else ""
    application_message = " ".join(args) if args else None

    application = "\n".join([
        f"Application Received",
        f"   User: {sender}{user_suffix}",
        f"   Position: {position_prefix}Admin",
        f"   Message: {application_message}",
        f"To hire this user, use /hire."
    ])

    receipt = (
        "Your application was received. Hopefully the response doesn't start with: \"After careful"
        " consideration...\""
    )

    # Gather recipients
    if sender_privilege == Privilege.Admin:
        recipients = [room.owner]
    else:
        recipients = []
        for adminship in await async_filter(Admin, room=room, is_limited=False):
            recipients += [await async_get(OBUser, adminship=adminship)]

    # Send the application and receipt
    await send_system_room_message(application, room, recipients)
    await send_system_room_message(receipt, room, [sender])
