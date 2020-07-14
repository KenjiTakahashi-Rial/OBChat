"""
A user must have Unlimited Admin privileges of the room to perform this command
(see OB.models.Admin & OB.constants.Privilege).
"""

from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import try_get
from OB.utilities.event import send_system_room_message

async def fire(args, sender, room):
    """
    Description:
        Removes one or more existing Admin database objects. The user may not issue admin-level
            commands in the target room, only user-level.

    Arguments:
        args (list[string]): The usernames of OBUsers to fire. Should have length 1 or more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # Check for initial errors
    if await async_get_privilege(sender, room) < Privilege.UnlimitedAdmin:
        error_message = (
            "That's a little outside your pay-grade. Only Unlimited Admins may fire admins. Try to"
            " /apply to be Unlimited."
        )
    elif len(args) == 0:
        error_message = "Usage: /fire <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room)
        return

    valid_fires = []
    error_messages = []

    for username in args:
        arg_user = try_get(OBUser, username=username)
        arg_admin = try_get(Admin, user=arg_user)

        # Check for per-argument errors
        if not arg_user:
            error_messages += (
                "\"{username}\" does not exist. You can't fire a ghost... can you?"
            )
        elif arg_user == sender:
            error_messages += (
                "You can't fire yourself. I don't care how bad your performance reviews are."
            )
        elif arg_user == room.owner:
            error_messages += f"That's the owner. You know, your BOSS. Nice try."
        elif not arg_admin:
            error_messages += (
                f"\"{username}\" is just a regular ol' user, so you can't fire them. You can /ban "
                "them if you want."
            )
        elif sender != room.owner and not arg_admin.is_limited:
            error_messages += (
                f"\"{username}\" is an Unlimited Admin, so you can't fire them. Please direct all "
                "complaints to your local room owner, I'm sure they'll love some more paperwork to"
                " do...")
        else:
            valid_fires += (arg_user, arg_admin)

    # Remove admin(s) and notify all parties that a user was fired
    send_to_sender = error_messages
    send_to_others = []

    # Fire valid fires (if any) and notify all parties that a user was fired
    for fired_user in valid_fires:
        fired_user[1].delete()

        await send_system_room_message(f"Clean out your desk. You lost your adminship at "
                                       "\"{room.name}\".", room)

        send_to_sender += f"It had to be done. You fired \"{fired_user[0].username}\""
        send_to_others += f"{fired_user[0].username} was fired! Those budget cuts are killer."

    if send_to_sender:
        await send_system_room_message("\n".join(send_to_sender), room, [sender])
    if send_to_others:
        await send_system_room_message("\n".join(send_to_others), room)
