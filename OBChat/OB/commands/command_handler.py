from OB.utilities import get_group_name, send_chat_message

from OB.enums import GroupTypes
from .user_level import create_room, who, private
from .admin_level import kick, ban, lift_ban
from .unlimited_admin_level import hire, fire
from .owner_level import delete_room

# Separate the commands that do the same things into columns
# pylint: disable=bad-whitespace
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

# Descriptions of the valid commands
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

def handle_command(data, user, room_name):
    # Separate by whitespace to get arguments
    separated = data.split()
    command_name = separated[0]
    args = separated[1:]

    try:
        COMMANDS[command_name](args, user, room_name)
    except KeyError:
        # Invalid command, send the list of valid commands
        send_chat_message(VALID_COMMANDS, get_group_name(GroupTypes.Room, room_name))
