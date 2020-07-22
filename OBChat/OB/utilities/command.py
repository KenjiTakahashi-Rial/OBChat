"""
Storage for database functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

from channels.db import database_sync_to_async

from OB.commands.command_handler import COMMANDS
from OB.constants import Privilege
from OB.models import Admin
from OB.utilities.database import try_get

def is_command_format(command):
    """
    Description:
        Determins if a string is formatted as a command or normal message. Command format is any
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
    Description:
        Determins if a string is a valid command. Valid commands are both in command format (see
        is_command_format()) and are contained in the COMMANDS dict constant.


    Arguments:
        command (string): The string to determine is or is not a valid command.

    Return values:
        boolean: True if the string is in command format and the command is in the COMMANDS dict.
    """

    return is_command_format(command) and command[1:] in COMMANDS

@database_sync_to_async
def async_get_privilege(user, room):
    """
    Description:
        Determines the highest privilege level of a user for a room.

    Arguments:
        username (string): The username of the OBUser to find the privilege of.
        room (Room): The database object of the room to find privilege for.

    Return values:
        The Privilege of the user for the room.
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
