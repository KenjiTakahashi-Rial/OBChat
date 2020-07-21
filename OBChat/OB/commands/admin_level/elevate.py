"""
A user must have Admin privileges of the room to perform this command (see OB.models.Admin &
OB.constants.Privilege).
"""

from OB.constants import Privilege
from OB.models import Admin, Ban, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_filter, async_model_list, async_try_get
from OB.utilities.event import send_system_room_message

async def elevate(args, sender, room):
    """
    Description:
        Requests an action (e.g. /kick, /ban, /lift) be performed by a user with higher privilege.
        Can request generally to all users with higher privilege or to a specific user.

    Arguments:
        args (list[string]): The command to elevate, the arguments of that command, and the user to
            elevate to (defaults to all users of higher privilege)
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # Remove duplicates
    args = list(dict.fromkeys(args))

    error_message = ""
    sender_privilege = await async_get_privilege(sender, room)

    # Check for initial errors
    if not sender.is_authenticated or sender.is_anon:
        error_message = (
            "Why don't you make an account or log in first? Call us old-fashiond, but anons have "
            "very little privileges around these parts."
        )
    elif sender_privilege < Privilege.Admin:
        error_message = (
            "Elevation is a skill that only Admins are capable of wielding. You have yet to reach "
            "the level of Admin - come back when you're ready!"
        )
    elif not args or not args[0][0] != ['('] or not args[0][-1] != [')']:
        error_message = "Usage: /elevate (<command>) <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_elevations = []
    error_messages = []

    if not args:
        # Get all users with higher privilege
        if sender_privilege < Privilege.UnlimitedAdmin:
            unlimited_admins = await async_filter(Admin, room=room, is_limited=False)
            valid_elevations += unlimited_admins
        valid_elevations += [room.owner]
        elevated_to_all = True
    else:
        # Check for per-argument errors
        for username in args:
            arg_user = await async_try_get(OBUser, username=username)

            if arg_user:
                arg_privilege = await async_get_privilege(arg_user, room)

            if not arg_user or arg_user not in await async_model_list(room.occupants):
                error_messages += [f"Nobody named {username} in this room. Are you seeing things?"]
            elif arg_user == sender:
                error_messages += [f"You can't elevate to yourself. Who do you think you are?"]
            elif arg_privilege < Privilege.UnlimitedAdmin:
                error_messages += [
                    f"{username} does not have more privileges than you. What's the point of "
                    "/elevate -ing do them?"
                ]
            else:
                valid_elevations += [arg_user]

        elevated_to_all = False

    receipt_body = [
        "    Recipients:" + ", ".join(valid_elevations),
        "    Command requested: ",
    ]


    send_to_sender = [
        "Sent an elevation request:\n",

    ]
    send_to_targets = [
        f"Received an elevation request from {sender}:",
        "    Recipients:"
    ]

    for elevation_user in valid_elevations:
        # Construct the responses
        send_to_sender += [f"{elevation_user} "]
        send_to_targets += [f"{elevation_user} "]
