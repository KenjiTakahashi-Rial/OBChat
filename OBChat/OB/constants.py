from .commands import *

DISPLAY_NAME_MAX_LENGTH = 15
ROOM_NAME_MAX_LENGTH = 15
MESSAGE_MAX_LENGTH = 100

# Command cases dictionary
COMMANDS = {
      "/room": room,                "/r": room,
      "/who": who,                  "/w": who,
      "/private": private,          "/p": private,
      "/hire": hire,                "/h": hire,
      "/fire": fire,                "/f": fire,
      "/kick": kick,                "/k": kick,
      "/ban": ban,                  "/b": ban,
      "/lift": lift_ban,            "/l": lift_ban,
      "/delete": delete_room,       "/d": delete_room
}

# Descriptions of the valid commands
VALID_COMMANDS = ("Valid commands:\n" +
                  " * /room - Create a new room\n" +
                  " * /who <room> - See who is in a room. Default: current room\n" +
                  " * /private <user> <message> - Send a private message\n" +
                  " * /hire <user1> <user2> ... - Make user(s) admins of your current room\n" +
                  " * /fire <user1> <user2> ... - Revoke admin privileges for user(s)\n" +
                  " * /kick <user1> <user2> ... - Kick user(s) from your current room\n" +
                  " * /ban <user1> <user2> ... - Ban user(s) from your current room\n" +
                  " * /lift <user1> <user2> ... - Lift ban on user(s) from your current room\n" +
                  " * /delete <name> - Delete a room. Default: current room\n" +
                  " * Typing backslash with only the first letter of a command works as well\n" +
                  " * To use backslash without a command: //\n" +
                  "End valid commands")
