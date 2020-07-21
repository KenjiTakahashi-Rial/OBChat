"""
A user must have Admin privileges of the room to perform this command (see OB.models.Admin &
OB.constants.Privilege).
"""

from OB.commands.command_handler import COMMANDS
from OB.constants import Privilege
from OB.models import Admin, Ban, OBUser
from OB.utilities.command import async_get_privilege, is_command
from OB.utilities.database import async_delete, async_filter, async_model_list, async_try_get
from OB.utilities.event import send_system_room_message

async def elevate(args, sender, room):
    """
    Description:
        Requests an action (e.g. /kick, /ban, /lift) be performed by a user with higher privilege.
        Can request generally to all users with higher privilege or to a specific user.

    Arguments:
        args (list[string]): The command to elevate, the arguments of that command, and the user to
            elevate to (defaults to all users of higher privilege).
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
    else:
        has_correct_syntax, command, targets, message = parse(args)

        if not has_correct_syntax:
            error_message = (
                "Usage: /elevate (<command> <arg1> <arg2> ...) (<user1> <user2> ...) (<message>)"
            )

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_elevations = []
    error_messages = []

    if not targets:
        # Get all users with higher privilege
        if sender_privilege < Privilege.UnlimitedAdmin:
            unlimited_admins = await async_filter(Admin, room=room, is_limited=False)
            valid_elevations += unlimited_admins
        valid_elevations += [room.owner]
    else:
        # Check for per-argument errors
        for username in targets:
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

    # Construction the elevation request
    elevation_body = [
        f"    Recipients:" + ", ".join(valid_elevations),
        f"    Command requested: {command}",
        f"    Message: {message if message else None}"
    ]

    send_to_sender = ["Sent an elevation request:\n"] + elevation_body
    send_to_targets = [f"Received an elevation request from {sender}\n:" + elevation_body]

    # Send the elevation request
    await send_system_room_message("\n".join(send_to_sender), room, [sender])
    await send_system_room_message("\n".join(send_to_targets), room, valid_elevations)

async def parse(args):
    """
    Description:
        Parses the arguments into 2 key parts: the command to elevate with its arguments and the
        target users to send the elevation request to.

    Arguments:
        args (list[string]): The command to elevate, the arguments of that command, and the target
        users to elevate to (defaults to all users of higher privilege).

    Return values:
        tuple(boolean, string, list[OBUser]): A tuple containing a boolean indicating that there
            were no syntax errors, a string of the command to elevate with its arguments and a list
            of the target users to send the elevation request to. If there is a syntax error,
            returns (False, "", []).
    """

    # Check for initial syntax errors
    if args[0][0] != '(' or not is_command(args[0][1:]) or args[0][1:] not in COMMANDS:
        return (False, "", [])

    # Reconstruct the command string
    command = args[0][1:]
    for i in range(1, len(args)):
        if args[i][-1] == ')':
            if i == 1:
                # There are no arguments for the requested command
                return (False, "", [])

            command += [args[i][:-1]]
            targets = [] if i + 1 == len(args) else args[i + 1:]
            return command, targets

        command += [args[i]]

    # There was no end parenthesis
    return (False, "", [])
