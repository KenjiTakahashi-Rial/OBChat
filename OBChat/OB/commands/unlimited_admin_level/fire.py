"""
fire function container module
"""

from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_save, async_try_get
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

    # Remove duplicates
    args = list(dict.fromkeys(args))

    error_message = ""
    sender_privilege = await async_get_privilege(sender, room)

    # Check for initial errors
    if sender_privilege < Privilege.UnlimitedAdmin:
        error_message = (
            "That's a little outside your pay-grade. Only Unlimited Admins may fire admins. Try to"
            " /apply to be Unlimited."
        )
    elif len(args) == 0:
        error_message = "Usage: /fire <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_fires = []
    error_messages = []

    # Check for per-argument errors
    for username in args:
        arg_user = await async_try_get(OBUser, username=username)
        arg_admin = await async_try_get(Admin, user=arg_user)

        if not arg_user:
            error_messages += [f"{username} does not exist. You can't fire a ghost... can you?"]
        elif arg_user == sender:
            error_messages += [
                "You can't fire yourself. I don't care how bad your performance reviews are."
            ]
        elif arg_user == room.owner:
            error_messages += ["That's the owner. You know, your BOSS. Nice try."]
        elif not arg_admin:
            error_messages += [
                f"{username} is just a regular ol' user, so you can't fire them. You can /kick or "
                "/ban them if you want."
            ]
        elif not arg_admin.is_limited and sender_privilege < Privilege.Owner:
            error_messages += [
                f"{username} is an Unlimited Admin, so you can't fire them. Please direct all "
                "complaints to your local room owner, I'm sure they'll love some more paperwork to"
                " do..."
            ]
        else:
            valid_fires += [{"user": arg_user, "adminship": arg_admin}]

    send_to_sender = error_messages + [("\n" if error_messages else "") + "Fired:"]
    send_to_targets = ["One or more users have been fired:"] # TODO: Change this to only send when more than one user is fired at once
    send_to_others = ["One or more users have been fired:"]

    for fired_user in valid_fires:
        if fired_user["adminship"].is_limited:
            # Remove the adminship
            await async_delete(fired_user["adminship"])
        else:
            # Make the adminship limited
            fired_user["adminship"].is_limited = True
            await async_save(fired_user["adminship"])

        send_to_sender += [f"    {fired_user}"]
        send_to_targets += [f"    {fired_user}"]
        send_to_others += [f"    {fired_user}"]

    if valid_fires:
        send_to_sender += ["It had to be done."]
        await send_system_room_message("\n".join(send_to_sender), room, [sender])

        send_to_targets += ["Clean out your desk."]
        await send_system_room_message("\n".join(send_to_sender), room, valid_fires)

        send_to_others += ["Those budget cuts are killer."]
        await send_system_room_message(
            "\n".join(send_to_others),
            room,
            exclusions=([sender] + valid_fires)
        )
    elif error_messages:
        await send_system_room_message("\n".join(error_messages), room, [sender])
