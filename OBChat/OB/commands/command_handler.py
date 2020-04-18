"""
Handles when a command is issued from a user and redirects to the appropriate command function.
"""

from OB.utilities import send_system_room_message

from .user_level import create_room, who, private
from .admin_level import kick, ban, lift_ban
from .unlimited_admin_level import hire, fire
from .owner_level import delete_room

# pylint: disable=bad-whitespace
# Separate the commands that do the same things into columns
# The values of this dict are command functions
COMMANDS = {
    "/room": create_room,   "/r": create_room,
    "/who": who,            "/w": who,
    "/private": private,    "/p": private,
    "/hire": hire,          "/h": hire,
    "/fire": fire,          "/f": fire,
    "/kick": kick,          "/k": kick,
    "/ban": ban,            "/b": ban,
    "/lift": lift_ban,      "/l": lift_ban,
    "/delete": delete_room, "/d": delete_room
}

VALID_COMMANDS = ("Valid commands:\n"
                  "    * /room - Create a new room\n"
                  "    * /who <room> - See who is in a room. Default: current room\n"
                  "    * /private <user> <message> - Send a private message\n"
                  "    * /hire <user1> <user2> ... - Make user(s) admins of your current room\n"
                  "    * /fire <user1> <user2> ... - Revoke admin privileges for user(s)\n"
                  "    * /kick <user1> <user2> ... - Kick user(s) from your current room\n"
                  "    * /ban <user1> <user2> ... - Ban user(s) from your current room\n"
                  "    * /lift <user1> <user2> ... - Lift ban on user(s) from your current room\n"
                  "    * /delete <name> - Delete a room. Default: current room\n"
                  "Type backslash with only the first letter of a command if you're in a hurry.\n"
                  "To use backslash without a command: //")

def handle_command(data, user, room):
    """
    Description:
        Tries to execute a command function from the COMMANDS dict with arguments.

    Arguments:
        data (string): A space-separated string of a command with arguments.
            ex: "/command arg1 arg2"
        user (OBUser): The OBUser database object from whom the command originated.
        room (Room): The Room database object from where the command originated.

    Return values:
        None
    """

    # Separate by whitespace to get arguments
    separated = data.split()
    command_name = separated[0]
    arguments = separated[1:]

    try:
        COMMANDS[command_name](arguments, user, room)
    except KeyError:
        # Invalid command, send the list of valid commands
        send_system_room_message(VALID_COMMANDS, room)
