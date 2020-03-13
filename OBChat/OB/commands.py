from channels.layers import get_channel_layer
from . import constants, models
from .consumers import ChatConsumer, GroupTypes


def command(request, room_name, input):
    # Separate by whitespace to get arguments
    separated = input.split()
    command = separated[0]
    args = separated[1:]

    try:
        constants.COMMANDS[command](request, args)
    except KeyError:
        group = ChatConsumer.GroupName(GroupTypes.Room, room_name)
        send(request, constants.VALID_COMMANDS, group)

def send(request, message, group):

    # Send message to room group
    async_to_sync(get_channel_layer().group_send) (
        group, # TODO: Get room name from url
        {
            "type": "receive_from_group",
            "message": message
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

#     send("Available rooms:", client)

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

#         send(room_str, client)

#     send("End list", client)

#     return True

def who(request, args):
    if not args:
        if room_name is None:
            send(request, "You're not in a room.")
            return

    if len(args) > 1:
        send(request, "Room name cannot contain spaces.")
        return

        # TODO: Get room name from url
        args.append("room_name")

    if not Room.objects.filter(name=args[0]).exists():
        send(request, f"\"{args[0]}\" doesn't exist, so that probably means nobody is in there.")
        return

    channel = get_channel_layer()
    group = Group(channel).channel_layer.group_channels(channel)
    if len(group) == 0:
        send(request, f"\"{args[0]}\" is all empty!")
        return

    # Iterate through users in room
    send(request, f"Users in: \"{args[0]}\" ({group})")

    room = Rooms.objects.get(name=room_name)

    for user in group:
        who_user = user.username

        # Tag user appropriately
        if user == room.owner:
            who_user += " (owner)"

        if Admin.objects.filter(user=user, room=room).exists():
            who_user += " (admin)"

        if user == request.user:
            who_user += " (you)"

        send(f" * {who_user}")

    send("End list")

# def leave(self, args, client, exit=False):
#     # Client is not in a room
#     if client.room is None:
#         send("Not in a room", client)

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
#         send(f"Left the room: {client.room.name}", client)

#     client.room.users.remove(client)
#     client.room = None

#     return True


def private(request, args):
    if not args:
        send("Usage: /private /<user> <message>")
    elif args[0][0] != '/':
        send("Looks like you forgot a \"/\" before the username. I'll let it slide.")

    user_query = User.objects.filter(username=args[0][1:])
    
    if not user_query.exists():
        send(f"\"{args[0]}\" doesn't exist. Your private message will broadcasted into space instead.", client)

    if len(args) == 1:
        send("No message specified. Did you give up halfway through?", client)
        return

    send_to = user_query[0]

    # Reconstruct message from args
    message = " ".join(args[1:])

    send(request, message, send_to)
    send(request, message, client)

def room(self, args, client):
    if not args:
        send("Usage: /room <name>", client)
    elif not request.user.is_authenticated:
        send("Identify yourself! Must log in to create a room.", client)
    elif len(args) > 1:
        send("Room name cannot contain spaces.", client)
    elif Room.objects.filter(name=room_name).exists():
        send(f"Someone beat you to it. \"{args[0]}\" already exists.")
    else:
        Room(name=room_name, owner=owner)
        send(f"Sold! Check out your new room: \"{args[0]}\"", client)

def hire(self, args):
    if client.username != client.room.owner:
        send("That's a little outside your pay-grade. Only Unlimited Admins may hire admins. Try to /apply to be unlimited.")

    if len(args) == 0:
        send("Usage: /admin <user1> <user2> ...", client)

    for username in args:
        if username not in self.passwords:
            if username not in self.usernames:
                send(f"\"{username}\" does not exist. Your imaginary friend needs an account before they can be an admin.")
            else:
                send(f"\"{username}\" hasn't signed up yet. they cannot be trusted with the immense responsibility that is adminship.")

        user = self.usernames[username]

        if username in client.room.admins:
            send(f"{username} already works for you. I can't believe you forgot. Did you mean /promote?")
            continue

        if username == client.username:
            send("You're already an admin, you can't be a DOUBLE admin.", client)
            continue

        client.room.admins.append(user.username)

        # Notify all parties that a user was made admin
        send(f"With great power comes great responsibility. You were promoted to admin in \"{client.room.name}\"!")
        send(f"Promoted {username} to admin. Keep an eye on them.", client)
        self.distribute(f"{username} was promoted to admin. Drinks on them!", [client.room.name], None, [client, user])

def fire(self, args, client):
    if len(args) == 0:
        send("Usage: /fire <user1> <user2> ...", client)
        return

    if True: # TODO: not unlimited or owner:
        print("There is an 'if True' here, preventing this command from resolvng.")
        send("That's a little outside your pay-grade. Only Unlimited Admins may fire admins. Try to /apply to be unlimited.")
        return

    for username in args:
        if username not in self.usernames and username not in self.passwords:
            send(f"\"{username}\" does not exist. You can't fire a ghost... can you?", client)
            continue

        if username not in client.room.admins:
            send(f"\"{username}\" is just a regular old user, so you can't fire them. You can /ban them if you want.", client)
            continue

        client.room.admins.remove(username)

        if username in self.usernames:
            send(f"Clean out your desk. You lost your adminship at \"{client.room.name}\".")

        send(f"It had to be done. You fired \"{username}\"", client)

        self.distribute(f"{username} was fired! Those budget cuts are killer.")


def kick(self, args, client):
    if len(args) == 0:
        send("Usage: /kick <user1> <user2> ...", client)
        return

    if client.username != client.room.owner:
        if client.username not in client.room.admins:
            send("That's a little outside your pay-grade. Only Unlimited Admins may fire admins. Try to /apply to be unlimited.")
            return

    for username in args:
        if username not in self.usernames and username not in self.passwords:
            send(f"Nobody named \"{username}\" in this room. Are you seeing things?", client)
            continue

        user = self.usernames[username]

        if username in client.room.admins:
            if client.username != client.room.owner:
                send("Insufficient privileges to kick admin: " +
                          f"{username}", client)

                no_errors = False
                continue

        # Do not allow users to kick themselves
        if username == client.username:
            send("Cannot kick self", client)

            no_errors = False
            continue

        # Owner cannot be kicked
        if username == client.room.owner:
            send(f"Cannot kick owner: {client.room.owner}",
                      client)

            no_errors = False
            continue

        # Actually remove the user
        user.room = None
        user.typing = ""
        client.room.users.remove(user)

        # Notify all parties that a user was kicked
        send(f"You were kicked from: {client.room.name}",
                  user)

        send(f"Kicked user: {username}", client)

        self.distribute(f"{username} was kicked",
                        [client.room.name], None, [client])

    return no_errors


def ban(self, args, client):
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
        send("Usage: /ban <user1> <user2> ...", client)

        return False

    if client.room is None:
        send("Not in a room", client)

        return False

    # Check privileges
    if client.username != client.room.owner:
        if client.username not in client.room.admins:
            send("Insufficient privileges to ban from: " +
                      client.room.name, client)

            return False

    no_errors = True

    for username in args:

        if username not in self.usernames and username not in self.passwords:
            send(f"User does not exist: {username}", client)

            no_errors = False
            continue

        if username in client.room.banned:
            send(f"User already banned: {username}", client)

            no_errors = False
            continue

        # Must be owner to ban admin
        if username in client.room.admins:
            if client.username != client.room.owner:
                send("Insufficient privileges to ban admin: " +
                          f"{username}", client)

                no_errors = False
                continue

        # Do not allow users to ban themselves
        if username == client.username:
            send("Cannot ban self", client)

            no_errors = False
            continue

        # Owner cannot be banned
        if username == client.room.owner:
            send(f"Cannot ban owner: {client.room.owner}",
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
            send(f"You were banned from: {client.room.name}",
                      user)

        send(f"Banned user: {username}", client)

        self.distribute(f"{username} was banned",
                        [client.room.name], None, [client])

    return no_errors


def lift_ban(self, args, client):
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
        send("Usage: /lift <user1> <user2> ...", client)

        return False

    if client.room is None:
        send("Not in a room", client)

        return False

    # Check privileges
    if client.username != client.room.owner:
        if client.username not in client.room.admins:
            send("Insufficient privileges to unban in: " +
                      client.room.name, client)

            return False

    no_errors = True

    for username in args:

        if username not in self.usernames and username not in self.passwords:
            send(f"User does not exist: {username}", client)

            no_errors = False
            continue

        if username not in client.room.banned:
            send(f"User not banned: {username}", client)

            no_errors = False
            continue

        # Must be owner to lift ban on admin
        if username in client.room.admins:
            if client.username != client.room.owner:
                send("Insufficient privileges to unban admin: " +
                          f"{username}", client)

                no_errors = False
                continue

        client.room.banned.remove(username)

        # Notify all parties that a user was banned
        if username in self.usernames:
            send(f"Your were unbanned from: {client.room.name}",
                      self.usernames[username])

        send(f"Unbanned user: {username}", client)

        self.distribute(f"{username} was unbanned",
                        [client.room.name], None, [client])

    return no_errors


def delete_room(self, args, client):
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
        send("Room name cannot contain spaces", client)

        return False

    if len(args) == 0:
        args.append(client.room.name)

    if args[0] not in self.rooms:
        send(f"Room does not exist: {args[0]}", client)

        return False

    if client.username != self.rooms[args[0]].owner:
        send(f"Insufficient privileges to delete: {args[0]}", client)

        return False

    # Get the room object
    room = self.rooms[args[0]]

    for user in room.users:
        user.room = None
        user.typing = ""

        if user.username != room.owner:
            send(f"The room was deleted: {room.name}", user)

    del self.rooms[args[0]]

    send(f"Deleted room: {args[0]}", client)

    return True
