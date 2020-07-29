"""
/ban command functions container module.
"""

from OB.constants import Privilege
from OB.models import Ban, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_get_owner, async_save, async_try_get
from OB.utilities.event import send_room_event, send_system_room_message

async def ban(args, sender, room):
    """
    Remove one or more OBConsumers from the group a Room is associated with and do not allow
    them to rejoin the group. Bans may be lifted (see lift()).

    Arguments:
        args (list[string]): The usernames of OBUsers to ban. Should have length 1 or more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # Remove duplicates
    args = list(dict.fromkeys(args))

    # Check for initial errors
    initial_error_message = check_initial_errors(args, sender, room)

    # Send initial error message back to user and cancel the command
    if initial_error_message:
        await send_system_room_message(initial_error_message, room, [sender])
        return

    # Check the validity of the arguments
    valid_bans, arg_error_messages = check_arguments(args, sender, room)

    # Execute the bans
    sender_receipt, occupants_notification = execute_bans(
        valid_bans,
        arg_error_messages,
        sender,
        room
    )

    # Send messages if applicable
    if sender_receipt:
        await send_system_room_message(sender_receipt, room, [sender])

    if occupants_notification:
        await send_system_room_message(occupants_notification, room, exclusions=[sender])

async def check_initial_errors(args, sender, room):
    """
    Check for initial errors such as lack of privilege or invalid syntax.

    Arguments:
        args (list[string]): The usernames of OBUsers to ban. Should have length 1 or more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.

    Return values:
        string: Returns an appropriate error message string. If there are no errors, returns the
            empty string.
    """

    error_message = ""
    sender_privilege = await async_get_privilege(sender, room)

    if sender_privilege < Privilege.AuthUser:
        # Is an anonymous/unauthenticated user
        error_message = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "banning people."
        )
    elif sender_privilege < Privilege.Admin:
        # Is authenticated, but not an admin
        error_message = (
            "That's a little outside your pay-grade. Only admins may ban users. Try to /apply to "
            "be an Admin."
        )
    elif not args:
        # Missing target arguments
        error_message = "Usage: /ban <user1> <user2> ..."

    return error_message

async def check_arguments(args, sender, room):
    """
    Check each argument for errors such as self-targeting or targeting a user of higher privilege.

    Arguments:
        args (list[string]): The usernames of OBUsers to ban. Should have length 1 or more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.

    Return values:
        tuple(list[OBUser], list[string]): Returns a tuple of a list of OBUsers to ban and a list
            of error messages to send to the sender.
    """

    valid_bans = []
    error_messages = []

    for username in args:
        arg_user = await async_try_get(OBUser, username=username)
        arg_privilege = None if not arg_user else await async_get_privilege(arg_user, room)

        if not arg_user:
            # Target user does not exist
            error_messages += [f"Nobody named {username} in this room. Are you seeing things?"]
        elif arg_user == sender:
            # Target user is the sender, themself
            error_messages += [
                f"You can't ban yourself. Just leave the room. Or put yourself on time-out."
            ]
        elif arg_user == await async_get_owner(room):
            # Target user is the owner
            error_messages += [f"That's the owner. You know, your BOSS. Nice try."]
        elif arg_privilege >= await async_get_privilege(sender, room):
            # Target user has Privilege greater than or equal to the sender
            job_title = "Admin"

            if arg_privilege == await async_get_privilege(sender, room):
                job_title += " just like you"

            if arg_privilege == Privilege.UnlimitedAdmin:
                job_title = "Unlimited " + job_title

            error_messages += [
                f"{arg_user} is an {job_title}, so you can't ban them. Feel free to "
                "/elevate your complaints to someone who has more authority."
            ]
        else:
            # Target user is a valid ban
            valid_bans += [arg_user]

    return valid_bans, error_messages

async def execute_bans(bans, arg_error_messages, sender, room):
    """
    Kick and ban users from the room.
    Constructs strings to send back to the sender and to the other occupants of the room.

    Arguments:
        bans (list[OBUser]): List of users to ban. Assumes that the validity of these users being
            banned has already been checked.
        arg_error_messages (list[string]): A list of argument error message strings (see
            check_arguments()).
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.

    Return values:
        tuple(string, string): Returns a tuple of a sender receipt string and a room occupant
            notification string.
    """

    if not bans:
        # Send the argument error messages back to the sender if there are any
        # Do not create a notification for other occupants
        return "\n".join(arg_error_messages) if arg_error_messages else "", ""

    # Prepend the argument error messages to the sender's receipt
    sender_receipt = arg_error_messages + [("\n" if arg_error_messages else "") + "Banned:"]
    occupants_notification = ["One or more users have been banned:"]

    for banned_user in bans:
        # Save the ban to the database
        await async_save(
            Ban,
            user=banned_user,
            room=room,
            issuer=sender
        )

        # Kick the user
        kick_event = {
            "type": "kick",
            "target_id": banned_user.id
        }

        await send_room_event(room.id, kick_event)

        sender_receipt += [f"   {banned_user}"]
        occupants_notification += [f"   {banned_user}"]

    sender_receipt += ["That'll show them."]
    occupants_notification += ["Let this be a lesson to you all."]

    return "\n".join(sender_receipt), "\n".join(occupants_notification)
