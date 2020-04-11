from enum import Enum

DISPLAY_NAME_MAX_LENGTH = 15
MESSAGE_MAX_LENGTH = 100
ROOM_NAME_MAX_LENGTH = 15
SYSTEM_USERNAME = "OB-Sys"

class GroupTypes(Enum):
    Invalid = 0
    Line = 1
    Room = 2
    Private = 3

class SystemOperations(Enum):
    Invalid = 0
    Kick = 1

class Privilege(Enum):
    Invalid = 0
    User = 0
    Admin = 1
    UnlimitedAdmin = 2
    Owner = 3
