from OB.models import Admin, OBUser
from OB.utilities import send_system_room_message, send_room_event

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

    valid_kicks = []
    error_messages = []

    admin_query = Admin.objects.filter(username=user.username)
    is_admin = user == room.owner or admin_query.exists()
    is_unlimited = user == room.owner or (admin_query.exists() and admin_query.is_unlimited)

    if not is_admin:
        error_messages += "That's a little outside your pay-grade. Only admins may kick users. \
            Try to /apply to be an admin."
    if len(args) == 0:
        error_messages += "Usage: /kick <user1> <user2> ..."
    else:
        for username in args:
            user_query = OBUser.objects.filter(username=username)
            admin_query = Admin.objects.filter(user=user_query.first())

            if not user_query.exists():
                error_messages += f"Nobody named \"{username}\" in this room. Are you seeing \
                    things?"
            elif user == user_query.first():
                error_messages += f"You can't kick yourself. Just leave the room. Or put \
                    yourself on time-out."
            elif user_query.first() == room.owner:
                error_messages += f"That's the owner. You know, your BOSS. Nice try."
            elif admin_query.exists() and not is_unlimited:
                error_messages += f"\"{username}\" is an unlimited admin, so you can't fire them.\
                    Please direct all complaints to your local room owner, I'm sure they'll \
                    love some more paperwork to do..."
            else:
                valid_kicks += user_query

    # Remove user(s) and notify all parties that a user was kicked
    send_to_sender = error_messages
    send_to_others = []

    kick_event = {"type": "kick"}

    for kicked_user in valid_kicks:
        kick_event["target"] = kicked_user
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
