from OB.enums import GroupTypes
from OB.models import Admin, Room, OBUser
from OB.utilities import get_group_name, send_chat_message, send_system_operation

def kick(args, user, room_name):
    current_room = Room.objects.get(room_name)
    valid_kicks = []
    error_messages = []

    admin_query = Admin.objects.filter(username=user.username)
    is_admin = user == current_room.owner or admin_query.exists()
    is_unlimited = user == current_room.owner or (admin_query.exists() and admin_query.is_unlimited)

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
                error_messages += f"Nobody named \"{username}\" in this room. Are you seeing things?"
            elif user == user_query.first():
                error_messages += f"You can't kick yourself. Just leave the room. Or put \
                    yourself on time-out."
            elif user_query.first() == current_room.owner:
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

    room_group = get_group_name(GroupTypes.Room, room_name)

    for kicked_user in valid_kicks:
        send_system_operation(SystemOperations.Kick, kicked_user, room_group)

        send_chat_message(f"You were kicked from {room_name}. Check yourself before you wreck yourself.", get_group_name(GroupTypes.Line, kicked_user.username))

        send_to_sender += f"Kicked {kicked_user.username} from {room_name}. That'll show them."
        send_to_others += f"{kicked_user.username} was kicked from the room. Let this be a lesson to you all."

    if send_to_sender:
        send_chat_message("\n".join(send_to_sender), get_group_name(GroupTypes.Line, user.username))
    if send_to_others:
        send_chat_message("\n".join(send_to_others), room_group)

def ban(args, user, room_name):
    """
    Description:
        Ban one or more users from a room
        Must have adminship or ownership
    Arguments:
        A Server object
        A list of arguments
        The client object that issued the command
    Return Value:
        True if the command was carried out
        False if an error occurred
    """

    if len(args) == 0:
        send_chat_message("Usage: /ban <user1> <user2> ...", client)

        return False

    if client.room is None:
        send_chat_message("Not in a room", client)

        return False

    # Check privileges
    if client.username != client.room.owner:
        if client.username not in client.room.admins:
            send_chat_message("Insufficient privileges to ban from: " +
                      client.room.name, client)

            return False

    no_errors = True

    for username in args:

        if username not in self.usernames and username not in self.passwords:
            send_chat_message(f"User does not exist: {username}", client)

            no_errors = False
            continue

        if username in client.room.banned:
            send_chat_message(f"User already banned: {username}", client)

            no_errors = False
            continue

        # Must be owner to ban admin
        if username in client.room.admins:
            if client.username != client.room.owner:
                send_chat_message("Insufficient privileges to ban admin: " +
                          f"{username}", client)

                no_errors = False
                continue

        # Do not allow users to ban themselves
        if username == client.username:
            send_chat_message("Cannot ban self", client)

            no_errors = False
            continue

        # Owner cannot be banned
        if username == client.room.owner:
            send_chat_message(f"Cannot ban owner: {client.room.owner}",
                      client)

            no_errors = False
            continue

        # Get user object
        user = self.usernames[username]

        # Remove the user first
        if user in client.room.users:
            user.room = None
            user.typing = ""
            client.room.users.remove(user)

        client.room.banned.append(user.username)

        # Notify all parties that a user was banned
        if username in self.usernames:
            send_chat_message(f"You were banned from: {client.room.name}",
                      user)

        send_chat_message(f"Banned user: {username}", client)

        self.distribute(f"{username} was banned",
                        [client.room.name], None, [client])

    return no_errors


def lift_ban(args, user, room_name):
    """
    Description:
        Lift ban on a user from a room
        Must have adminship or ownership
    Arguments:
        A Server object
        A list of arguments
        The client object that issued the command
    Return Value:
        True if the command was carried out
        False if an error occurred
    """

    if len(args) == 0:
        send_chat_message("Usage: /lift <user1> <user2> ...", client)

        return False

    if client.room is None:
        send_chat_message("Not in a room", client)

        return False

    # Check privileges
    if client.username != client.room.owner:
        if client.username not in client.room.admins:
            send_chat_message("Insufficient privileges to unban in: " +
                      client.room.name, client)

            return False

    no_errors = True

    for username in args:

        if username not in self.usernames and username not in self.passwords:
            send_chat_message(f"User does not exist: {username}", client)

            no_errors = False
            continue

        if username not in client.room.banned:
            send_chat_message(f"User not banned: {username}", client)

            no_errors = False
            continue

        # Must be owner to lift ban on admin
        if username in client.room.admins:
            if client.username != client.room.owner:
                send_chat_message("Insufficient privileges to unban admin: " +
                          f"{username}", client)

                no_errors = False
                continue

        client.room.banned.remove(username)

        # Notify all parties that a user was banned
        if username in self.usernames:
            send_chat_message(f"Your were unbanned from: {client.room.name}",
                      self.usernames[username])

        send_chat_message(f"Unbanned user: {username}", client)

        self.distribute(f"{username} was unbanned",
                        [client.room.name], None, [client])

    return no_errors