"""
Each of these classes is a user command.
Commands are issued by users when using the command syntax (see
OB.utilities.command.is_command_format()).
"""

from OB.commands.admin_level import ban
from OB.commands.admin_level import lift
from OB.commands.admin_level import kick
from OB.commands.auth_user_level import apply
from OB.commands.auth_user_level import create
from OB.commands.base import BaseCommand
from OB.commands.owner_level import delete
from OB.commands.unlimited_admin_level import hire
from OB.commands.unlimited_admin_level import fire
from OB.commands.user_level import who
from OB.commands.user_level import private

# pylint: disable=bad-whitespace
# Justification: Commands mapped to the same function are put into columns for readability.
# The values of this dict are command functions
COMMANDS = {
    "/apply": apply,        "/a": apply,
    "/ban": ban,            "/b": ban,
    "/create": create,      "/c": create,
    "/delete": delete,      "/d": delete,
    "/fire": fire,          "/f": fire,
    "/hire": hire,          "/h": hire,
    "/kick": kick,          "/k": kick,
    "/lift": lift,          "/l": lift,
    "/private": private,    "/p": private,
    "/who": who,            "/w": who,
}
