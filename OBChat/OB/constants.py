"""
These are enums and constant variables used by more than one other file.
"""

from enum import IntEnum

SYSTEM_USERNAME = "OB-Sys"
ANON_PREFIX = "OB-Anon-"

class GroupTypes(IntEnum):
    Invalid = 0
    Line = 1
    Room = 2
    Private = 3

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

class Privilege(IntEnum):
    Invalid = 0
    User = 0
    AuthUser = 1
    Admin = 2
    UnlimitedAdmin = 3
    Owner = 4
