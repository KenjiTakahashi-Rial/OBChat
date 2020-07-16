"""
A user must have Unlimited Admin privileges of the room to perform this command
(see OB.models.Admin & OB.constants.Privilege).
"""

import channels

from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_save, async_try_get
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

    # Remove duplicates
    args = list(dict.fromkeys(args))

    error_message = ""
    sender_privilege = await async_get_privilege(sender, room)

    # Check for initial errors
    if sender_privilege < Privilege.UnlimitedAdmin:
        error_message = (
            "That's a little outside your pay-grade. Only Unlimited Admins may hire admins. Try to"
            " /apply to be Unlimited."
        )
    elif len(args) == 0:
        error_message = "Usage: /hire <user1> <user2> ..."

    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_hires = []
    error_messages = []

    for username in args:
        arg_user = await async_try_get(OBUser, username=username)
        arg_admin = await async_try_get(Admin, user=arg_user)

        # Check for per-argument errors
        if not arg_user:
            error_messages += [
                f"{username} does not exist. Your imaginary friend needs an account before "
                "they can be an Admin."
            ]
        elif arg_user == sender:
            error_messages += [
                "You can't hire yourself. I don't care how good your letter of recommendation is."
            ]
        elif arg_user == room.owner:
            error_messages += ["That's the owner. You know, your BOSS. Nice try."]
        elif not arg_user.is_authenticated or arg_user.is_anon:
            error_messages += [
                f"{username} hasn't signed up yet. They cannot be trusted with the immense "
                "responsibility that is adminship."
            ]
        elif arg_admin:
            if not arg_admin.is_limited:
                error_messages += [
                    f"{username} is already an Unlimited Admin. There's nothing left to /hire them"
                    " for."
                ]
            elif sender_privilege < Privilege.Owner:
                error_messages += [
                    f"{username} is already an Admin. Only the owner may promote them to Unlimited"
                    " Admin."
                ]
        else:
            valid_hires += [arg_user]

    send_to_sender = error_messages
    send_to_others = []

    for hired_user in valid_hires:
        if arg_admin and sender_privilege == Privilege.Owner:
            # Make the Admin unlimited
            arg_admin.is_limited = False
            await async_save(arg_admin)
            admin_prefix = "Unlimited "
        else:
            # Make the user an admin
            await async_save(
                Admin,
                user=hired_user,
                room=room,
                issuer=sender
            )
            admin_prefix = ""

        await send_system_room_message(
            f"With great power comes great responsibility. You were promoted to {admin_prefix}"
            f"Admin in {room.name}!",
            room,
            [hired_user]
        )

        send_to_sender += [
            f"Promoted {hired_user.username} to {admin_prefix}Admin in {room.name}. Keep an eye on"
            " them."
        ]
        send_to_others += [
            f"{hired_user.username} was promoted to {admin_prefix}Admin. Drinks on them!"
        ]

    if send_to_sender:
        await send_system_room_message("\n".join(send_to_sender), room, [sender])
    if send_to_others:
        await send_system_room_message("\n".join(send_to_others), room, exclusions=[sender])
