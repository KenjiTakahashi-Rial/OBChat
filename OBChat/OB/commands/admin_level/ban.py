"""
A user must have Admin privileges of the room to perform this command (see OB.models.Admin &
OB.constants.Privilege).
"""

from OB.constants import Privilege
from OB.models import Ban, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_get_owner, async_model_list, async_save, \
    async_try_get
from OB.utilities.event import send_room_event, send_system_room_message

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
    sender_privilege = await async_get_privilege(sender, room)

    # Check for initial errors
    if not sender.is_authenticated or sender.is_anon:
        error_message = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "banning people."
        )
    elif sender_privilege < Privilege.Admin:
        error_message = (
            "That's a little outside your pay-grade. Only admins may ban users. Try to /apply to "
            "be an Admin."
        )
    elif not args:
        error_message = "Usage: /ban <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_bans = []
    error_messages = []

    # Check for per-argument errors
    for username in args:
        arg_user = await async_try_get(OBUser, username=username)

        if arg_user:
            arg_privilege = await async_get_privilege(arg_user, room)

        if not arg_user or arg_user not in await async_model_list(room.occupants):
            error_messages += [f"Nobody named {username} in this room. Are you seeing things?"]
        elif arg_user == sender:
            error_messages += [
                f"You can't ban yourself. Just leave the room. Or put yourself on time-out."
            ]
        elif arg_user == await async_get_owner(room):
            error_messages += [f"That's the owner. You know, your BOSS. Nice try."]
        elif arg_privilege >= sender_privilege:
            job_title = "Admin"

            if arg_privilege == sender_privilege:
                job_title += " just like you"

            if arg_privilege == Privilege.UnlimitedAdmin:
                job_title = "Unlimited " + job_title

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
