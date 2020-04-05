from enum import Enum

class GroupTypes(Enum):
    Invalid = 0
    Line = 1
    Room = 2
    Private = 3

class SystemOperations(Enum):
    Invalid = 0
    Kick = 1
