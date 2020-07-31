"""
Each of these functions is a user command.
Commands are issued by users when using the command syntax (see
OB.utilities.command.is_command_format()).
"""

from OB.commands.admin_level.ban import ban
from OB.commands.base import BaseCommand
from OB.commands.admin_level.lift import lift
from OB.commands.admin_level.kick import kick
from OB.commands.auth_user_level.apply import apply
from OB.commands.auth_user_level.create import create
from OB.commands.owner_level.delete import delete
from OB.commands.unlimited_admin_level.hire import hire
from OB.commands.unlimited_admin_level.fire import fire
from OB.commands.user_level.who import who
from OB.commands.user_level.private import private

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
