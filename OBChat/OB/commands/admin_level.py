"""
A user must have admin privileges of the room to perform these commands (see OB.models.Admin &
OB.utilities.command.get_privilege()).
"""

from OB.constants import Privilege
from OB.models import Ban, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_get_owner, async_model_list, async_save, \
    async_try_get
from OB.utilities.event import send_room_event, send_system_room_message

async def kick(args, sender, room):
    """
    Description:
        Remove one or more OBConsumers from the group a Room is associated with. They will not
        receive messages from the group until they rejoin the Room.

    Arguments:
        args (list[string]): The usernames of OBUsers to kick. Should have length 1 or more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was issued in.
    """

    # Remove duplicates
    args = list(dict.fromkeys(args))

    error_message = ""

    # Check for initial errors
    if not sender.is_authenticated or sender.is_anon:
        error_message = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "kicking people."
        )
    elif await async_get_privilege(sender, room) < Privilege.Admin:
        error_message = (
            "That's a little outside your pay-grade. Only admins may kick users. Try to /apply to "
            "be an admin."
        )
    elif not args:
        error_message = "Usage: /kick <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_kicks = []
    error_messages = []

    for username in args:
        arg_user = await async_try_get(OBUser, username=username)

        if arg_user:
            arg_privilege = await async_get_privilege(arg_user, room)
            sender_privilege = await async_get_privilege(sender, room)

        # Check for per-argument errors
        if not arg_user or arg_user not in await async_model_list(room.occupants):
            error_messages += [f"Nobody named {username} in this room. Are you seeing things?"]
        elif arg_user == sender:
            error_messages += [
                f"You can't kick yourself. Just leave the room. Or put yourself on time-out."
            ]
        elif arg_user == await async_get_owner(room):
            error_messages += [f"That's the owner. You know, your BOSS. Nice try."]
        elif arg_privilege >= sender_privilege:
            job_title = "admin"

            if arg_privilege == sender_privilege:
                job_title += " just like you"

            if arg_privilege == Privilege.UnlimitedAdmin:
                job_title = "unlimited " + job_title

            error_messages += [
                f"{arg_user} is an {job_title}, so you can't kick them. Feel free to "
                "/elevate your complaints to someone who has more authority."
            ]
        else:
            valid_kicks += [arg_user]

    send_to_sender = error_messages + [("\n" if error_messages else "") + "Kicked:"]
    send_to_others = ["One or more users have been kicked:"]

    for kicked_user in valid_kicks:
        # Kick the user
        kick_event = {
            "type": "kick",
            "target_id": kicked_user.id
        }

        await send_room_event(room.id, kick_event)

        # Notify others that a user was kicked
        send_to_sender += [f"   {kicked_user}"]
        send_to_others += [f"   {kicked_user}"]

    if valid_kicks:
        send_to_sender += ["That'll show them."]
        await send_system_room_message("\n".join(send_to_sender), room, [sender])

        send_to_others += ["Let this be a lesson to you all."]
        await send_system_room_message("\n".join(send_to_others), room)
    elif error_messages:
        await send_system_room_message("\n".join(error_messages), room, [sender])

async def ban(args, sender, room):
    """
    Description:
        Remove one or more OBConsumers from the group a Room is associated with and do not allow
        them to rejoin the group. Bans may be lifted (see lift()).

    Arguments:
        args (list[string]): The usernames of OBUsers to ban. Should have length 1 or more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # Remove duplicates
    args = list(dict.fromkeys(args))

    error_message = ""

    # Check for initial errors
    if not sender.is_authenticated or sender.is_anon:
        error_message = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "banning people."
        )
    elif await async_get_privilege(sender, room) < Privilege.Admin:
        error_message = (
            "That's a little outside your pay-grade. Only admins may ban users. Try to /apply to "
            "be an admin."
        )
    elif not args:
        error_message = "Usage: /ban <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_bans = []
    error_messages = []

    for username in args:
        arg_user = await async_try_get(OBUser, username=username)

        if arg_user:
            arg_privilege = await async_get_privilege(arg_user, room)
            sender_privilege = await async_get_privilege(sender, room)

        # Check for per-argument errors
        if not arg_user or arg_user not in await async_model_list(room.occupants):
            error_messages += [f"Nobody named {username} in this room. Are you seeing things?"]
        elif arg_user == sender:
            error_messages += [
                f"You can't ban yourself. Just leave the room. Or put yourself on time-out."
            ]
        elif arg_user == await async_get_owner(room):
            error_messages += [f"That's the owner. You know, your BOSS. Nice try."]
        elif arg_privilege >= sender_privilege:
            job_title = "admin"

            if arg_privilege == sender_privilege:
                job_title += " just like you"

            if arg_privilege == Privilege.UnlimitedAdmin:
                job_title = "unlimited " + job_title

            error_messages += [
                f"{arg_user} is an {job_title}, so you can't ban them. Feel free to "
                "/elevate your complaints to someone who has more authority."
            ]
        else:
            valid_bans += [arg_user]

    send_to_sender = error_messages + [("\n" if error_messages else "") + "Banned:"]
    send_to_others = ["One or more users have been banned:"]

    for banned_user in valid_bans:
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

        # Notify others that a user was banned
        send_to_sender += [f"   {banned_user}"]
        send_to_others += [f"   {banned_user}"]

    if valid_bans:
        send_to_sender += ["That'll show them."]
        await send_system_room_message("\n".join(send_to_sender), room, [sender])

        send_to_others += ["Let this be a lesson to you all."]
        await send_system_room_message("\n".join(send_to_others), room)
    elif error_messages:
        await send_system_room_message("\n".join(error_messages), room, [sender])

async def lift(args, sender, room):
    """
    Description:
        Allow one or more OBConsumers from a group a Room is associated with to rejoin a Room after
        being banned. Viewing the user from inside the Room will show they have been banned before.

    Arguments:
        args (list[string]): The usernames of OBUsers whose bans to lift. Should have length 1 or
            more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # Remove duplicates
    args = list(dict.fromkeys(args))

    error_message = ""

    # Check for initial errors
    if not sender.is_authenticated or sender.is_anon:
        error_message = (
            "You are far from one who can lift bans. Log in and prove yourself an admin."
        )
    elif await async_get_privilege(sender, room) < Privilege.Admin:
        error_message = (
            "A mere mortal like yourself does not have the power to lift bans. Try to /apply to be"
            " an admin and perhaps you may obtain this power if you are worthy."
        )
    elif not args:
        error_message = "Usage: /lift <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_lifts = []
    error_messages = []

    for username in args:
        arg_user = await async_try_get(OBUser, username=username)

        if arg_user:
            arg_ban = await async_try_get(Ban, user=arg_user, room=room)
            issuer = await async_try_get(OBUser, ban_issued=arg_ban)
            issuer_privilege = await async_get_privilege(issuer, room)
            sender_privilege = await async_get_privilege(sender, room)
        else:
            arg_ban = None

        # Check for per-argument errors
        if not arg_user or not arg_ban:
            error_messages += [
                f"No user named {username} has been banned from this room. How can "
                "one lift that which has not been banned?"
            ]
        elif issuer_privilege >= sender_privilege and issuer != sender:
            error_messages += [
                f"{username} was banned by {issuer}. You cannot lift a ban issued by a "
                "user of equal or higher privilege than yourself. If you REALLY want to lift this "
                "ban you can /elevate to a higher authority."
            ]
        else:
            valid_lifts += [(arg_ban, arg_user)]

    send_to_sender = error_messages + [("\n" if error_messages else "") + "Ban lifted:"]

    for lifted_ban, lifted_user in valid_lifts:
        # Delete the ban from the database
        await async_delete(lifted_ban)

        send_to_sender += [f"   {lifted_user}"]

    if valid_lifts:
        send_to_sender += ["Fully reformed and ready to integrate into society."]
        await send_system_room_message("\n".join(send_to_sender), room, [sender])
    elif error_messages:
        await send_system_room_message("\n".join(error_messages), room, [sender])

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

    # TODO: Implement this
