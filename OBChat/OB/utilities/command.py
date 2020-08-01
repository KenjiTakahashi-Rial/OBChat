"""
Useful command functions.
"""

from channels.db import database_sync_to_async

import OB.commands

from OB.constants import Privilege
from OB.models import Admin
from OB.utilities.database import try_get

def is_command_format(command):
    """
    Determines if a string is formatted as a command or normal message. Command format is any
    string with a single '/' in front.

    Arguments:
        command (string): The string to determine is or is not command format.

    Return values:
        boolean: True if the string is in command format.
    """

    if len(command) > 1:
        return command[0] == '/' and command[1] != '/'

    return command and command[0] == '/'

def is_valid_command(command):
    """
    Determines if a string is a valid command. Valid commands are both in command format (see
    is_command_format()) and are contained in the COMMANDS dict constant.

    Arguments:
        command (string): The string to determine is or is not a valid command.

    Return values:
        boolean: True if the string is in command format and the command is in the COMMANDS dict.
    """

    return is_command_format(command) and command[1:] in OB.commands.COMMANDS

def get_privilege(user, room):
    """
    Determines the highest privilege level of a user for a room.

    Arguments:
        username (string): The username of the OBUser to find the privilege of.
        room (Room): The database object of the room to find privilege for.

    Return values:
        Privilege: The Privilege of the user for the room.
    """

    if user == room.owner:
        return Privilege.Owner

    admin_object = try_get(Admin, user=user)

    if admin_object:
        if not admin_object.is_limited:
            return Privilege.UnlimitedAdmin

        return Privilege.Admin

    if user.is_authenticated and not user.is_anon:
        return Privilege.AuthUser

    return Privilege.User

@database_sync_to_async
def async_get_privilege(user, room):
    """
    See OB.utilities.command.get_privilege().
    """

    get_privilege(user, room)
