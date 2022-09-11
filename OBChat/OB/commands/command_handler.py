"""
Handles when a command is issued from a user and redirects to the appropriate command function.
"""

from OB.commands.base import BaseCommand
from OB.commands.commands import CALLER_MAP
from OB.commands.commands import COMMANDS
from OB.models.ob_user import OBUser
from OB.models.room import Room
from OB.utilities.event import send_system_room_message

MANUAL_ENTRIES: str = "\n\t* ".join([command.MANUAL for command in COMMANDS])
VALID_COMMANDS: str = (
    f"Valid commands:\n"
    f"\t* {MANUAL_ENTRIES}\n"
    f"Type backslash with only the first letter of a command if you're in a hurry.\n"
    f"To use backslash as the first character of a message: //"
)


async def handle_command(command: str, sender: OBUser, room: Room) -> None:
    """
    Tries to execute a command function from the COMMANDS dict with arguments.
    Assumes that the text given is in command format (see
    OB.utilities.command.is_command_format()).

    Arguments:
        command (string): A space-separated string of a command with arguments.
            ex: "/command arg1 arg2"
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # Separate by whitespace to get arguments
    separated: list[str] = command.split()
    caller: str = separated[0]
    arguments: list[str] = separated[1:]

    if caller in CALLER_MAP:
        command_class: BaseCommand = CALLER_MAP[caller]
        command_instance = command_class(arguments, sender, room)
        await command_instance.execute()
    else:
        # Invalid command, send the list of valid commands
        await send_system_room_message(VALID_COMMANDS, room, [sender])
