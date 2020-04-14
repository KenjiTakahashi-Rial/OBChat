from OB.models import Admin, OBUser
from OB.utilities import send_system_room_message

def hire(args, user, room):
    valid_hires = []
    error_messages = []

    is_unlimited = user == room.owner or Admin.objects.filter(
        username=user.username, is_unlimited=True).exists()

    if not is_unlimited:
        error_messages += "That's a little outside your pay-grade. Only unlimited admins may \
            hire admins. Try to /apply to be unlimited."
    elif len(args) == 0:
        error_messages += "Usage: /admin <user1> <user2> ..."
    else:
        for username in args:
            user_query = OBUser.objects.filter(username=username)
            admin_query = Admin.objects.filter(user=user_query.first())

            if not user_query.exists():
                error_messages += f"\"{username}\" does not exist. Your imaginary friend needs an \
                    account before they can be an admin."
            elif user == user_query.first():
                error_messages += f"You can't hire yourself. I don't care how good your \
                    letter of recommendation is."
            elif user_query.first() == room.owner:
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
        new_admin_object = Admin(user=hired_user, room=room)
        new_admin_object.save()

        send_system_room_message(f"With great power comes great responsibility. You were promoted to admin in \"\
            {room.name}\"!", room)

        send_to_sender += f"Promoted {hired_user.username} to admin in {room.name}. Keep an eye on them."
        send_to_others += f"{hired_user.username} was promoted to admin. Drinks on them!"

    if send_to_sender:
        send_system_room_message("\n".join(send_to_sender), room)
    if send_to_others:
        send_system_room_message("\n".join(send_to_others), room)

def fire(args, user, room):
    valid_fires = []
    error_messages = []

    is_unlimited = user == room.owner or Admin.objects.filter(
        username=user.username, is_unlimited=True).exists()

    if not is_unlimited:
        error_messages += "That's a little outside your pay-grade. Only unlimited admins may \
            fire admins. Try to /apply to be unlimited."
    elif len(args) == 0:
        error_messages += "Usage: /fire <user1> <user2> ..."
    else:
        for username in args:
            user_query = OBUser.objects.filter(username=username)
            admin_query = Admin.objects.filter(user=user_query.first())

            if not user_query.exists():
                error_messages += "\"{username}\" does not exist. You can't fire a ghost... can \
                    you?"
            elif user == user_query.first():
                error_messages += "You can't fire yourself. I don't care how bad your \
                    performance reviews are."
            elif user_query.first() == room.owner:
                error_messages += f"That's the owner. You know, your BOSS. Nice try."
            elif not admin_query.exists():
                error_messages += f"\"{username}\" is just a regular old user, so you can't fire \
                    them. You can /ban them if you want."
            elif not user == room.owner and  not admin_query.first().is_limited:
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

        send_system_room_message(f"Clean out your desk. You lost your adminship at \"{room.name}\".",
            room)

        send_to_sender += f"It had to be done. You fired \"{fired_user[0].username}\""
        send_to_others += f"{fired_user[0].username} was fired! Those budget cuts are killer."

    if send_to_sender:
        send_system_room_message("\n".join(send_to_sender), room)
    if send_to_others:
        send_system_room_message("\n".join(send_to_others), room)
