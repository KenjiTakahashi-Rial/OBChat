"""
lift function container module
"""

from OB.constants import Privilege
from OB.models import Ban, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_try_get
from OB.utilities.event import send_system_room_message

async def lift(args, sender, room):
    """
    Allow one or more OBConsumers from a group a Room is associated with to rejoin a Room after
    being banned.
    TODO: Viewing a user from inside the Room will show they have been banned before.

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
            "You are far from one who can lift bans. Log in and prove yourself an Admin."
        )
    elif await async_get_privilege(sender, room) < Privilege.Admin:
        error_message = (
            "A mere mortal like yourself does not have the power to lift bans. Try to /apply to be"
            " an Admin and perhaps you may obtain this power if you are worthy."
        )
    elif not args:
        error_message = "Usage: /lift <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_lifts = []
    error_messages = []

    # Check for per-argument errors
    for username in args:
        arg_user = await async_try_get(OBUser, username=username)

        if arg_user:
            arg_ban = await async_try_get(Ban, user=arg_user, room=room)
            issuer = await async_try_get(OBUser, ban_issued=arg_ban)
            issuer_privilege = await async_get_privilege(issuer, room)
            sender_privilege = await async_get_privilege(sender, room)
        else:
            arg_ban = None

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
