"""
These are enums and constant variables used by more than one other file.
"""

from enum import Enum

SYSTEM_USERNAME = "OB-Sys"
ANON_PREFIX = "OB-Anon-"

class GroupTypes(Enum):
    Invalid = 0
    Line = 1
    Room = 2
    Private = 3

class Privilege(Enum):
    Invalid = 0
    User = 0
    Admin = 1
    UnlimitedAdmin = 2
    Owner = 3
