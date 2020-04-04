from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from . import constants, models
from .consumers import ChatConsumer, GroupTypes, get_group_name, SystemOperations

def command(data, user, room_name):
    # Separate by whitespace to get arguments
    separated = data.split()
    command_name = separated[0]
    args = separated[1:]

    try:
        constants.COMMANDS[command_name](args, user, room_name)
    except KeyError:
        # Invalid command, send the list of valid commands
        send_chat_message(constants.VALID_COMMANDS, room_name)

def send_chat_message(message, group):
    async_to_sync(get_channel_layer().group_send)(
        group,
        {
            "type": "chat_message",
            "message": message
        }
    )

def send_system_operation(operation, user, group):
    async_to_sync(get_channel_layer().group_send)(
        group,
        {
            "type": "system_operation",
            "operation": operation,
            "user": user
        }
    )

# def show_rooms(self, args, client):
#     """
#     Description:
#         Display the available rooms
#     Arguments:
#         A Server object
#         A list of arguments
#         The client object that issued the command
#     Return Value:
#         True if the command was carried out
#         False if an error occurred
#     """

#     send_chat_message("Available rooms:", client)

#     for room in self.rooms:
#         room_str = f" * {room} ({len(self.rooms[room].users)})"

#         # Get room object
#         room = self.rooms[room]

#         # Tag room appropriately
#         if client.username in room.admins:
#             room_str += " (admin)"

#         if client.username == room.owner:
#             room_str += " (owner)"

#         if client.room == room:
#             room_str += " (current)"

#         if client.username in room.banned:
#             room_str += " (banned)"

#         send_chat_message(room_str, client)

#     send_chat_message("End list", client)

#     return True

def who(args, user, room_name):
    if not args and room_name is None:
        error_message = "You're not in a room."
    elif len(args) > 1:
        error_message = "Room name cannot contain spaces."
    else:
        args.append(room_name)

    if not models.Room.objects.filter(name=args[0]).exists():
        error_message = f"\"{args[0]}\" doesn't exist, so that probably means nobody is in there."
    else:
        # TODO: Get the room's list of current users

        if False: # TODO: len(current_users) == 0:
            error_message = f"\"{args[0]}\" is all empty!"

    group_name = get_group_name(GroupTypes.Room, room_name)

    if error_message:
        send_chat_message(error_message, group_name)
        return

    # Iterate through users in room
    user_list = f"Users in: \"{args[0]}\" ({group_name})\n"

    current_room = models.Room.objects.get(name=room_name)

    for group_user in group:
        who_user = group_user.username

        # Tag user appropriately
        if group_user == current_room.owner:
            user_list += " (owner)"

        if models.Admin.objects.filter(user=user, room=room).exists():
            user_list += " (admin)"

        if group_user == user:
            user_list += " (you)"

        user_list += f"\n * {who_user}\nEnd list"

    send_chat_message(user_list, group)

# def leave(self, args, client, exit=False):
#     # Client is not in a room
#     if client.room is None:
#         send_chat_message("Not in a room", client)

#         return False

#     leave_user = client.username
#     # Tag user appropriately
#     if client.username == client.room.owner:
#         leave_user += " (owner)"

#     if client.username in client.room.admins:
#         leave_user += " (admin)"

#     self.distribute(f"{leave_user} left the room", [client.room.name],
#                     None, [client])

#     # Don't print the leave message when exiting
#     if not exit:
#         send_chat_message(f"Left the room: {client.room.name}", client)

#     client.room.users.remove(client)
#     client.room = None

#     return True


def private(args, user, room_name):
    if not args:
        error_message = "Usage: /private /<user> <message>"
    elif args[0][0] != '/':
        error_message = "Looks like you forgot a \"/\" before the username. I'll let it slide."
    else:
        user_query = models.User.objects.filter(username=args[0][1:])

    if not user_query.exists():
        error_message = f"\"{args[0]}\" doesn't exist. Your private message will broadcasted \
            into space instead."
    elif len(args) == 1:
        error_message = "No message specified. Did you give up halfway through?"

    if error_message:
        send_chat_message(error_message, room_name)
        return

    send_to = user_query.first()

    # Reconstruct message from args
    message = " ".join(args[1:])

    send_chat_message(message, get_group_name(GroupTypes.Private, user.username, send_to.username))

def room(args, user, room_name):
    if not args:
        return_message = "Usage: /room <name>"
    elif not user.is_authenticated:
        return_message = "Identify yourself! Must log in to create a room."
    elif len(args) > 1:
        return_message = "Room name cannot contain spaces."
    elif models.Room.objects.filter(name=room_name).exists():
        return_message = f"Someone beat you to it. \"{args[0]}\" already exists."
    else:
        models.Room(name=room_name, owner=user).save()
        return_message = f"Sold! Check out your new room: \"{args[0]}\""

    send_chat_message(return_message, get_group_name(GroupTypes.Room, room_name))

def hire(args, user, room_name):
    current_room = models.Room.objects.get(room_name)
    valid_hires = []
    error_messages = []

    is_unlimited = user == current_room.owner or models.Admin.objects.filter(
        username=user.username, is_unlimited=True).exists()
    
    if not is_unlimited:
        error_messages += "That's a little outside your pay-grade. Only unlimited admins may \
            hire admins. Try to /apply to be unlimited."
    elif len(args) == 0:
        error_messages += "Usage: /admin <user1> <user2> ..."
    else:
        for username in args:
            user_query = models.User.objects.filter(username=username)
            admin_query = models.Admin.objects.filter(user=user_query.first())
            
            if not user_query.exists():
                error_messages += f"\"{username}\" does not exist. Your imaginary friend needs an \
                    account before they can be an admin."
            elif user == user_query.first():
                error_messages += f"You can't hire yourself. I don't care how good your \
                    letter of recommendation is."
            elif user_query.first() == current_room.owner:
                error_messages += f"That's the owner. You know, your BOSS. Nice try."
            elif False: # TODO: check for anonymous user
                error_messages += f"\"{username}\" hasn't signed up yet. they cannot be trusted \
                    with the immense responsibility that is adminship."
            elif admin_query.exists():
                error_messages += f"{username} already works for you. I can't believe you \
                    forgot. Did you mean /promote?"
            else:
                valid_hires += user_query

    # Add admin(s) and notify all parties that a user was hired
    send_to_sender = error_messages
    send_to_others = []

    for hired_user in valid_hires:
        models.Admin(user=hired_user, room=current_room).save()

        send_chat_message(f"With great power comes great responsibility. You were promoted to admin in \"\
            {room_name}\"!", get_group_name(GroupTypes.Line, hired_user.username))
        
        send_to_sender += f"Promoted {hired_user.username} to admin in {room_name}. Keep an eye on them."
        send_to_others += f"{hired_user.username} was promoted to admin. Drinks on them!"

    if send_to_sender:
        send_chat_message("\n".join(send_to_sender), get_group_name(GroupTypes.Line, user.username))
    if send_to_others:
        send_chat_message("\n".join(send_to_others), get_group_name(GroupTypes.Room, room_name))

def fire(args, user, room_name):
    current_room = models.Room.objects.get(room_name)
    valid_fires = []
    error_messages = []

    is_unlimited = user == current_room.owner or models.Admin.objects.filter(
        username=user.username, is_unlimited=True).exists()

    if not is_unlimited:
        error_messages += "That's a little outside your pay-grade. Only unlimited admins may \
            fire admins. Try to /apply to be unlimited."
    elif len(args) == 0:
        error_messages += "Usage: /fire <user1> <user2> ..."
    else:
        for username in args:
            user_query = models.User.objects.filter(username=username)
            admin_query = models.Admin.objects.filter(user=user_query.first())

            if not user_query.exists():
                error_messages += "\"{username}\" does not exist. You can't fire a ghost... can \
                    you?"
            elif user == user_query.first():
                error_messages += "You can't fire yourself. I don't care how bad your \
                    performance reviews are."
            elif user_query.first() == current_room.owner:
                error_messages += f"That's the owner. You know, your BOSS. Nice try."
            elif not admin_query.exists():
                error_messages += f"\"{username}\" is just a regular old user, so you can't fire \
                    them. You can /ban them if you want."
            elif not user == current_room.owner and  not admin_query.first().is_limited:
                error_messages += f"\"{username}\" is an unlimited admin, so you can't fire them.\
                     lease direct all complaints to your local room owner, I'm sure they'll \
                    love some more paperwork to do..."
            else:
                valid_fires += (user_query, admin_query)
            
    # Remove admin(s) and notify all parties that a user was fired
    send_to_sender = error_messages
    send_to_others = []
    
    for fired_user in valid_fires:
        fired_user[1].delete()

        send_chat_message(f"Clean out your desk. You lost your adminship at \"{room_name}\".",  
            get_group_name(GroupTypes.Line, fired_user[0].username)) 

        send_to_sender += f"It had to be done. You fired \"{fired_user[0].username}\""
        send_to_others += f"{fired_user[0].username} was fired! Those budget cuts are killer."

    if send_to_sender:
        send_chat_message("\n".join(send_to_sender), get_group_name(GroupTypes.Line, user.username))
    if send_to_others:
        send_chat_message("\n".join(send_to_others), get_group_name(GroupTypes.Room, room_name))

def kick(args, user, room_name):
    current_room = models.Room.objects.get(room_name)
    valid_kicks = []
    error_messages = []

    admin_query = models.Admin.objects.filter(username=user.username)
    is_admin = user == current_room.owner or admin_query.exists()
    is_unlimited = user == current_room.owner or (admin_query.exists() and admin_query.is_unlimited)

    if not is_admin:
        error_messages += "That's a little outside your pay-grade. Only admins may kick users. \
            Try to /apply to be an admin."
    if len(args) == 0:
        error_messages += "Usage: /kick <user1> <user2> ..."
    else:
        for username in args:
            user_query = models.User.objects.filter(username=username)
            admin_query = models.Admin.objects.filter(user=user_query.first())

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


def delete_room(args, user, room_name):
    """
    Description:
        Delete a room
        Must have ownership
    Arguments:
        A Server object
        A list of arguments
        The client object that issued the command
    Return Value:
        True if the command was carried out
        False if an error occurred
    """

    if len(args) > 1:
        send_chat_message("Room name cannot contain spaces", client)

        return False

    if len(args) == 0:
        args.append(client.room.name)

    if args[0] not in self.rooms:
        send_chat_message(f"Room does not exist: {args[0]}", client)

        return False

    if client.username != self.rooms[args[0]].owner:
        send_chat_message(f"Insufficient privileges to delete: {args[0]}", client)

        return False

    # Get the room object
    room = self.rooms[args[0]]

    for user in room.users:
        user.room = None
        user.typing = ""

        if user.username != room.owner:
            send_chat_message(f"The room was deleted: {room.name}", user)

    del self.rooms[args[0]]

    send_chat_message(f"Deleted room: {args[0]}", client)

    return True
