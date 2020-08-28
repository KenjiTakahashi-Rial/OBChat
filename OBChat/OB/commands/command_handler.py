"""
Handles when a command is issued from a user and redirects to the appropriate command function.
"""

import OB.commands

from OB.utilities.event import send_system_room_message

# TODO: Rework this to be held inside each command module
VALID_COMMANDS = "\n".join([
    "Valid commands:",
    f"    * {OB.commands.auth_user_level.create.CreateCommand.documentation}",
    f"    * {OB.commands.user_level.who.WhoCommand.documentation}",
    f"    * {OB.commands.user_level.private.PrivateCommand.documentation}",
    "    * /fire <user1> <user2> ... - Revoke Admin privileges for user(s)",
    "    * /kick <user1> <user2> ... - Kick user(s) from your current room",
    "    * /ban <user1> <user2> ... - Ban user(s) from your current room",
    "    * /lift <user1> <user2> ... - Lift ban on user(s) from your current room",
    "    * /delete <room1> <room2> ... - Delete a room. Default: current room",
    f"    * {OB.commands.unlimited_admin_level.hire.HireCommand.documentation}",
    "Type backslash with only the first letter of a command if you're in a hurry.",
    "To use backslash as the first character of a message: //"
])

async def handle_command(command, sender, room):
    """
    Tries to execute a command function from the COMMANDS dict with arguments.
    Assumes that the text given is in command format (see
    OB.utilities.command.is_command_format()).

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
        await OB.commands.COMMANDS[command_name](arguments, sender, room).execute()
    except KeyError:
        # Invalid command, send the list of valid commands
        await send_system_room_message(VALID_COMMANDS, room, [sender])
