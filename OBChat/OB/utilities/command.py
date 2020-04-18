"""
Storage for database functions that are called in multiple places and are not associated with any
particular instance of a class.
"""

from OB.constants import Privilege
from OB.models import Admin
from OB.utilities.database import try_get

def is_command(command):
    """
    Description:
        Determins if a string is a command or normal message. All commands are called by the user
        by prepending the command name with '/' or by typing '/' with only the first letter of the
        command name (see commands directory).

    Arguments:
        command (string): The string to determine is or is not a command.

    Return values:
        Returns true if the command parameter's argument is a command.
        Otherwise false.
    """
    if len(command) > 1:
        return command[0] == '/' and command[1] != '/'

    return command and command[0] == '/'

def get_privilege(user, room):
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
        if admin_object.is_limited:
            return Privilege.UnlimitedAdmin

        return Privilege.Admin

    return Privilege.User
