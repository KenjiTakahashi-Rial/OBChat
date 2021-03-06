"""
Each of these classes is a user command.
Commands are issued by users when using the command syntax (see
OB.utilities.command.is_command_format()).
"""

from OB.commands.command_handler import handle_command
from OB.commands.admin_level import BanCommand
from OB.commands.admin_level import ElevateCommand
from OB.commands.admin_level import KickCommand
from OB.commands.admin_level import LiftCommand
from OB.commands.auth_user_level import ApplyCommand
from OB.commands.auth_user_level import CreateCommand
from OB.commands.base import BaseCommand
from OB.commands.owner_level import DeleteCommand
from OB.commands.unlimited_admin_level import FireCommand
from OB.commands.unlimited_admin_level import HireCommand
from OB.commands.user_level import PrivateCommand
from OB.commands.user_level import WhoCommand

# pylint: disable=bad-whitespace
# Justification: Commands mapped to the same function are put into columns for readability.
# The values of this dict are command functions
COMMANDS = {
    "/apply": ApplyCommand,             "/a": ApplyCommand,
    "/ban": BanCommand,                 "/b": BanCommand,
    "/create": CreateCommand,           "/c": CreateCommand,
    "/delete": DeleteCommand,           "/d": DeleteCommand,
    "/elevate": ElevateCommand,         "/e": ElevateCommand,
    "/fire": FireCommand,               "/f": FireCommand,
    "/hire": HireCommand,               "/h": HireCommand,
    "/kick": KickCommand,               "/k": KickCommand,
    "/lift": LiftCommand,               "/l": LiftCommand,
    "/private": PrivateCommand,         "/p": PrivateCommand,
    "/who": WhoCommand,                 "/w": WhoCommand,
}
# pylint: enable=bad-whitespace
