"""
kick function container module
"""

from OB.constants import Privilege
from OB.models import OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_get_owner, async_model_list, async_try_get
from OB.utilities.event import send_room_event, send_system_room_message

async def kick(args, sender, room):
    """
    Remove one or more OBConsumers from the group a Room is associated with.
    Kicked users will not receive messages from the group until they rejoin the Room.

    Arguments:
        args (list[string]): The usernames of OBUsers to kick. Should have length 1 or more.
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was issued in.
    """

    # TODO: Add an option to do this silently (without notifying everyone)

    # Remove duplicates
    args = list(dict.fromkeys(args))

    error_message = ""
    sender_privilege = await async_get_privilege(sender, room)

    # Check for initial errors
    if not sender.is_authenticated or sender.is_anon:
        error_message = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "kicking people."
        )
    elif sender_privilege < Privilege.Admin:
        error_message = (
            "That's a little outside your pay-grade. Only admins may kick users. Try to /apply to "
            "be an Admin."
        )
    elif not args:
        error_message = "Usage: /kick <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room, [sender])
        return

    valid_kicks = []
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
                f"You can't kick yourself. Just leave the room. Or put yourself on time-out."
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
        await send_system_room_message("\n".join(send_to_others), room, exclusions=[sender])
    elif error_messages:
        await send_system_room_message("\n".join(error_messages), room, [sender])
