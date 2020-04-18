"""
A user must be an admin (see models.Admin) of the room to perform these commands.
"""

from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities import get_privilege, send_system_room_message, send_room_event, try_get

def kick(args, user, room):
    """
    Description:
        Remove one or more OBConsumers from the group a Room is associated with. They will not
        receive messages from the group until they rejoin the Room.

    Arguments:
        args (list[string]): The usernames of OBUsers to kick. Should have length 1 or more.
        user (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was issued in.

    Return values:
        None
    """

    # Check for initial errors
    if get_privilege(user, room) < Privilege.Admin:
        error_message = "That's a little outside your pay-grade. Only admins may kick \
            users. Try to /apply to be an admin."
    elif len(args) == 0:
        error_message = "Usage: /kick <user1> <user2> ..."
    
    # Send error message back to the issuing user
    if error_message:
        send_system_room_message(error_message, room)
        return

    valid_kicks = []
    error_messages = []

    for username in args:
        arg_user_object = try_get(OBUser, username=username)
        arg_admin_object = try_get(Admin, user=arg_user_object)

        # Check for per-argument errors
        if not arg_user_object or arg_user_object not in room.occupants:
            error_messages += f"Nobody named \"{username}\" in this room. Are you seeing \
                things?"
        elif arg_user_object == user:
            error_messages += f"You can't kick yourself. Just leave the room. Or put \
                yourself on time-out."
        elif arg_user_object == room.owner:
            error_messages += f"That's the owner. You know, your BOSS. Nice try."
        elif arg_admin_object and get_privilege(user, room) < Privilege.UnlimitedAdmin:
            error_messages += f"\"{username}\" is an unlimited admin, so you can't fire them.\
                Please direct all complaints to your local room owner, I'm sure they'll \
                love some more paperwork to do..."
        else:
            valid_kicks += arg_user_object

    send_to_sender = error_messages
    send_to_others = []

    # Execute valid kicks (if any) and notify all parties that a user was kicked
    for kicked_user in valid_kicks:
        kick_event = {
            "type": "kick",
            "target": kicked_user
        }

        send_room_event(room.name, kick_event)

        send_system_room_message(f"You were kicked from {room.name}. Check yourself before you \
            wreck yourself.", room)

        send_to_sender += f"Kicked {kicked_user.username} from {room.name}. That'll show them."
        send_to_others += f"{kicked_user.username} was kicked from the room. Let this be a lesson \
            to you all."

    if send_to_sender:
        send_system_room_message("\n".join(send_to_sender), room)
    if send_to_others:
        send_system_room_message("\n".join(send_to_others), room)

def ban(args, user, room):
    """
    Description:
        Remove one or more OBConsumers from the group a Room is associated with and do not allow
        them to rejoin the group. Bans may be lifted (see lift_ban()).

    Arguments:
        args (list[string]): The usernames of OBUsers to ban. Should have length 1 or more.
        user (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was issued in.

    Return values:
        None
    """

    # TODO: Implement this


def lift_ban(args, user, room):
    """
    Description:
        Allow one or more OBConsumers from a group a Room is associated with to rejoin a Room after
        being banned. Viewing the user from inside the Room will show they have been banned before.

    Arguments:
        args (list[string]): The usernames of OBUsers to hire. Should have length 1 or more.
        user (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was issued in.

    Return values:
        None
    """

    # TODO: Implement this
