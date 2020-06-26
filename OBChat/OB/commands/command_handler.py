"""
Handles when a command is issued from a user and redirects to the appropriate command function.
"""

from OB.commands.admin_level import kick, ban, lift
from OB.commands.auth_user_level import create
from OB.commands.owner_level import delete
from OB.commands.unlimited_admin_level import hire, fire
from OB.commands.user_level import who, private
from OB.utilities.event import send_system_room_message

# pylint: disable=bad-whitespace
# Justification: Commands mapped to the same function are put into columns for readability.
# The values of this dict are command functions
COMMANDS = {
    "/create": create,      "/c": create,
    "/who": who,            "/w": who,
    "/private": private,    "/p": private,
    "/hire": hire,          "/h": hire,
    "/fire": fire,          "/f": fire,
    "/kick": kick,          "/k": kick,
    "/ban": ban,            "/b": ban,
    "/lift": lift,          "/l": lift,
    "/delete": delete,      "/d": delete
}

VALID_COMMANDS = "\n".join([
    "Valid commands:",
    "    * /create - Create a new room",
    "    * /who <room1> <room2> ... - See who is in a room. Default: current room",
    "    * /private /<user> <message> - Send a private message",
    "    * /hire <user1> <user2> ... - Make user(s) admins of your current room",
    "    * /fire <user1> <user2> ... - Revoke admin privileges for user(s)",
    "    * /kick <user1> <user2> ... - Kick user(s) from your current room",
    "    * /ban <user1> <user2> ... - Ban user(s) from your current room",
    "    * /lift <user1> <user2> ... - Lift ban on user(s) from your current room",
    "    * /delete <room1> <room2> ... - Delete a room. Default: current room",
    "Type backslash with only the first letter of a command if you're in a hurry.",
    "To use backslash without a command: //"
])

async def handle_command(command, sender, room):
    """
    Description:
        Tries to execute a command function from the COMMANDS dict with arguments.
        Assumes that the text given is in command format (see OB.utilities.command.is_command()).

    Arguments:
        data (string): A space-separated string of a command with arguments.
            ex: "/command arg1 arg2"
        sender (OBUser): The OBUser who issued the command.
        room (Room): The Room the command was sent from.
    """

    # Separate by whitespace to get arguments
    separated = command.split()
    command_name = separated[0]
    arguments = separated[1:]

    try:
        await COMMANDS[command_name](arguments, sender, room)
    except KeyError:
        # Invalid command, send the list of valid commands
        await send_system_room_message(VALID_COMMANDS, room, sender)
