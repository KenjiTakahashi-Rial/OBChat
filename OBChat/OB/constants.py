"""
Constants used in various places throughout the app.
"""

from enum import IntEnum

class GroupTypes(IntEnum):
    """
    The GroupType of a Consumer determines the format of the Consumer's group name, which
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
    The different levels of privilege that a user has to perform commands in a Room (see
    OB.commands).
    Privilege varies between Rooms.
    """

    Invalid = 0
    User = 1
    AuthUser = 2
    Admin = 3
    UnlimitedAdmin = 4
    Owner = 5
