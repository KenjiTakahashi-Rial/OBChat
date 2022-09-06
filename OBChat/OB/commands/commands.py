from OB.commands.admin_level import BanCommand
from OB.commands.admin_level import ElevateCommand
from OB.commands.admin_level import KickCommand
from OB.commands.admin_level import LiftCommand
from OB.commands.auth_user_level import ApplyCommand
from OB.commands.auth_user_level import CreateCommand
from OB.commands.owner_level import DeleteCommand
from OB.commands.unlimited_admin_level import FireCommand
from OB.commands.unlimited_admin_level import HireCommand
from OB.commands.user_level import PrivateCommand
from OB.commands.user_level import WhoCommand


COMMANDS = [
    ApplyCommand,
    BanCommand,
    CreateCommand,
    DeleteCommand,
    ElevateCommand,
    FireCommand,
    HireCommand,
    KickCommand,
    LiftCommand,
    PrivateCommand,
    WhoCommand,
]

CALLER_MAP = {}
for command in COMMANDS:
    for caller in command.CALLERS:
        CALLER_MAP[f"/{caller}"] = command
