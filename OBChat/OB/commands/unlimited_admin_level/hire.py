"""
A user must have unlimited admin privileges of the room to perform this command
(see OB.models.Admin & OB.constants.Privilege).
"""

from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import try_get
from OB.utilities.event import send_system_room_message

async def hire(args, sender, room):
    """
    Description:
        Saves one or more new Admin database objects. The user may issue admin-level commands
            in the target room.

    Arguments:
        args (list[string]): The usernames of OBUsers to hire. Should have length 1 or more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # Check for initial errors
    if await async_get_privilege(sender, room) < Privilege.UnlimitedAdmin:
        error_message = (
            "That's a little outside your pay-grade. Only unlimited admins may hire admins. Try to"
            " /apply to be unlimited."
        )
    elif len(args) == 0:
        error_message = "Usage: /admin <user1> <user2> ..."

    if error_message:
        await send_system_room_message(error_message, room)
        return

    valid_hires = []
    error_messages = []

    for username in args:
        arg_user = try_get(OBUser, username=username)
        arg_admin = try_get(Admin, user=arg_user)

        # Check for per-argument errors
        if not arg_user:
            error_messages += (
                f"\"{username}\" does not exist. Your imaginary friend needs an account before "
                "they can be an admin."
            )
        elif arg_user == sender:
            error_messages += (
                f"You can't hire yourself. I don't care how good your letter of recommendation is."
            )
        elif arg_user == room.owner:
            error_messages += f"That's the owner. You know, your BOSS. Nice try."
        elif not sender.is_authenticated:
            error_messages += (
                f"\"{username}\" hasn't signed up yet. they cannot be trusted with the immense "
                "responsibility that is adminship."
            )
        elif arg_admin:
            error_messages += (
                f"{username} already works here. I can't believe you forgot. Did you mean "
                "/promote?"
            )
        else:
            valid_hires += arg_user

    send_to_sender = error_messages
    send_to_others = []

    # Make new Admin objects for valid hires (if any) and notify all parties that a user was hired
    for hired_user in valid_hires:
        Admin(
            sender=hired_user,
            room=room
        ).save()

        await send_system_room_message(
            f"With great power comes great responsibility. You were promoted to admin in "
            "\"{room.name}\"!",
            room,
            [hired_user]
        )

        send_to_sender += (
            f"Promoted {hired_user.username} to admin in {room.name}. Keep an eye on them."
        )
        send_to_others += f"{hired_user.username} was promoted to admin. Drinks on them!"

    if send_to_sender:
        await send_system_room_message("\n".join(send_to_sender), room, [sender])
    if send_to_others:
        await send_system_room_message("\n".join(send_to_others), room)
