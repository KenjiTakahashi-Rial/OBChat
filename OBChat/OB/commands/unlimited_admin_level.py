"""
A user must be an unlimited admin see (models.Admin.is_unlimited) of the room to perform these
commands.
"""

from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import get_privilege
from OB.utilities.database import try_get
from OB.utilities.event import send_system_room_message

async def hire(args, user, room):
    """
    Description:
        Saves one or more new Admin database objects. The user may issue admin-level commands
            in the target room.

    Arguments:
        args (list[string]): The usernames of OBUsers to hire. Should have length 1 or more.
        user (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was issued in.

    Return values:
        None.
    """

    # Check for initial errors
    if get_privilege(user, room) < Privilege.UnlimitedAdmin:
        error_message = "That's a little outside your pay-grade. Only unlimited admins may \
            hire admins. Try to /apply to be unlimited."
    elif len(args) == 0:
        error_message = "Usage: /admin <user1> <user2> ..."

    if error_message:
        await send_system_room_message(error_message, room)
        return

    valid_hires = []
    error_messages = []

    for username in args:
        arg_user_object = try_get(OBUser, username=username)
        arg_admin_object = try_get(Admin, user=arg_user_object)

        # Check for per-argument errors
        if not arg_user_object:
            error_messages += f"\"{username}\" does not exist. Your imaginary friend needs an \
                account before they can be an admin."
        elif arg_user_object == user:
            error_messages += f"You can't hire yourself. I don't care how good your \
                letter of recommendation is."
        elif arg_user_object == room.owner:
            error_messages += f"That's the owner. You know, your BOSS. Nice try."
        elif not user.is_authenticated:
            error_messages += f"\"{username}\" hasn't signed up yet. they cannot be trusted \
                with the immense responsibility that is adminship."
        elif arg_admin_object:
            error_messages += f"{username} already works here. I can't believe you \
                forgot. Did you mean /promote?"
        else:
            valid_hires += arg_user_object

    send_to_sender = error_messages
    send_to_others = []

    # Make new Admin objects for valid hires (if any) and notify all parties that a user was hired
    for hired_user in valid_hires:
        Admin(
            user=hired_user,
            room=room
        ).save()

        await send_system_room_message(f"With great power comes great responsibility. You were \
            promoted to admin in \"{room.name}\"!", room)

        send_to_sender += f"Promoted {hired_user.username} to admin in {room.name}. Keep an eye \
            on them."
        send_to_others += f"{hired_user.username} was promoted to admin. Drinks on them!"

    if send_to_sender:
        await send_system_room_message("\n".join(send_to_sender), room)
    if send_to_others:
        await send_system_room_message("\n".join(send_to_others), room)

async def fire(args, user, room):
    """
    Description:
        Removes one or more existing Admin database objects. The user may not issue admin-level
            commands in the target room, only user-level.

    Arguments:
        args (list[string]): The usernames of OBUsers to fire. Should have length 1 or more.
        user (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was issued in.

    Return values:
        None.
    """

    # Check for initial errors
    if get_privilege(user, room) < Privilege.UnlimitedAdmin:
        error_message = "That's a little outside your pay-grade. Only unlimited admins may \
            fire admins. Try to /apply to be unlimited."
    elif len(args) == 0:
        error_message = "Usage: /fire <user1> <user2> ..."

    # Send error message back to the issuing user
    if error_message:
        await send_system_room_message(error_message, room)
        return

    valid_fires = []
    error_messages = []

    for username in args:
        arg_user_object = try_get(OBUser, username=username)
        arg_admin_object = try_get(Admin, user=arg_user_object)

        # Check for per-argument errors
        if not arg_user_object:
            error_messages += "\"{username}\" does not exist. You can't fire a ghost... can \
                you?"
        elif arg_user_object == user:
            error_messages += "You can't fire yourself. I don't care how bad your \
                performance reviews are."
        elif arg_user_object == room.owner:
            error_messages += f"That's the owner. You know, your BOSS. Nice try."
        elif not arg_admin_object:
            error_messages += f"\"{username}\" is just a regular old user, so you can't fire \
                them. You can /ban them if you want."
        elif user != room.owner and not arg_admin_object.is_limited:
            error_messages += f"\"{username}\" is an unlimited admin, so you can't fire them.\
                please direct all complaints to your local room owner, I'm sure they'll \
                love some more paperwork to do..."
        else:
            valid_fires += (arg_user_object, arg_admin_object)

    # Remove admin(s) and notify all parties that a user was fired
    send_to_sender = error_messages
    send_to_others = []

    # Fire valid fires (if any) and notify all parties that a user was fired
    for fired_user in valid_fires:
        fired_user[1].delete()

        await send_system_room_message(f"Clean out your desk. You lost your adminship at \
            \"{room.name}\".", room)

        send_to_sender += f"It had to be done. You fired \"{fired_user[0].username}\""
        send_to_others += f"{fired_user[0].username} was fired! Those budget cuts are killer."

    if send_to_sender:
        await send_system_room_message("\n".join(send_to_sender), room)
    if send_to_others:
        await send_system_room_message("\n".join(send_to_others), room)
