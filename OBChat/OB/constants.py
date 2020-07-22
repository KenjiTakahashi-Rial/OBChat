"""
This module contains enums and constant variables used by more than one other file.
"""

from enum import IntEnum

SYSTEM_USERNAME = "OB-Sys"
ANON_PREFIX = "OB-Anon-"

class GroupTypes(IntEnum):
    """
    The GroupType of a Consumer determines the format of the Consumer's group name. This
    determines which events a Consumer will receive.
    """

    Invalid = 0
    Line = 1
    Room = 2
    Private = 3

    @classmethod
    def choices(cls):
        """
        Allows the enum to be used as a database model attribute (see OB.models).
        """

        return tuple((i.name, i.value) for i in cls)

class Privilege(IntEnum):
    """
    The different levels of privilege that a user has to perform commands in a Room. Privilege
    varies between Rooms.
    """

    Invalid = 0
    User = 0
    AuthUser = 1
    Admin = 2
    UnlimitedAdmin = 3
    Owner = 4
