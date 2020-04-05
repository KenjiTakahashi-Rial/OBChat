from OB.enums import GroupTypes
from OB.models import Admin, Room, User
from OB.utilities import get_group_name, send_chat_message

def who(args, user, room_name):
    if not args and room_name is None:
        error_message = "You're not in a room."
    elif len(args) > 1:
        error_message = "Room name cannot contain spaces."
    else:
        args.append(room_name)

    if not Room.objects.filter(name=args[0]).exists():
        error_message = f"\"{args[0]}\" doesn't exist, so that probably means nobody is in there."
    else:
        room_query = Room.objects.get(name=room_name)

        if len(room_query.occupants.all()) == 0:
            error_message = f"\"{args[0]}\" is all empty!"

    if error_message:
        send_chat_message(error_message, get_group_name(GroupTypes.Room, room_name))
        return

    # Iterate through users in room
    user_list = f"Users in: \"{args[0]}\" ({room_name})\n"

    room_query = Room.objects.get(name=room_name)

    for occupant in room_query.occupants.all():
        who_user = occupant.username

        # Tag user appropriately
        if occupant == room_query.owner:
            user_list += " (owner)"

        if Admin.objects.filter(user=user, room=room_query).exists():
            user_list += " (admin)"

        if occupant == user:
            user_list += " (you)"

        user_list += f"\n * {who_user}\nEnd list"

    send_chat_message(user_list, get_group_name(GroupTypes.Room, room_name))

def private(args, user, room_name):
    if not args:
        error_message = "Usage: /private /<user> <message>"
    elif args[0][0] != '/':
        error_message = "Looks like you forgot a \"/\" before the username. I'll let it slide."
    else:
        user_query = User.objects.filter(username=args[0][1:])

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

def create_room(args, user, room_name):
    if not args:
        return_message = "Usage: /room <name>"
    elif not user.is_authenticated:
        return_message = "Identify yourself! Must log in to create a room."
    elif len(args) > 1:
        return_message = "Room name cannot contain spaces."
    elif Room.objects.filter(name=room_name).exists():
        return_message = f"Someone beat you to it. \"{args[0]}\" already exists."
    else:
        Room(name=room_name, owner=user).save()
        return_message = f"Sold! Check out your new room: \"{args[0]}\""

    send_chat_message(return_message, get_group_name(GroupTypes.Room, room_name))
