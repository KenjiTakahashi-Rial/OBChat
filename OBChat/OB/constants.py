from .commands import *

DISPLAY_NAME_MAX_LENGTH = 15
ROOM_NAME_MAX_LENGTH = 15
MESSAGE_MAX_LENGTH = 100

# Command cases dictionary
COMMANDS = {"/rooms": show_rooms,         "/r": show_rooms,
            "/join": join,                "/j": join,
            "/who": who,                  "/w": who,
            "/leave": leave,              "/l": leave,
            "/private": private,          "/p": private,
            "/setpassword": password,     "/s": password,
            "/new": new,                  "/n": new,
            "/admin": admin,              "/a": admin,
            "/canceladmin": cancel_admin, "/c": cancel_admin,
            "/kick": kick,                "/k": kick,
            "/ban": ban,                  "/b": ban,
            "/unban": unban,              "/u": unban,
            "/delete": delete,            "/d": delete,
            "/exit": client_exit,         "/x": client_exit,
            "/quit": client_exit,         "/q": client_exit}

# Descriptions of the valid commands
VALID_COMMANDS = ("Valid commands:\n\r" +
                  " * /rooms - See active rooms\n\r" +
                  " * /join <room> - Join a room\n\r" +
                  " * /who <room> - See who is in a room. " +
                  "Default: current room \n\r" +
                  " * /leave - Leave your current room\n\r" +
                  " * /private <user> <message> - Send a " +
                  "private message\n\r" +
                  " * /setpassword - Set a password for your username\n\r" +
                  " * /new <name> - Create a new room\n\r" +
                  " * /admin <user1> <user2> ... - Make user(s) " +
                  " admins of your current room\n\r" +
                  " * /canceladmin <user1> <user2> ... - Revoke admin " +
                  "privileges for user(s)\n\r" +
                  " * /kick <user1> <user2> ... - Kick user(s) " +
                  "from your current room\n\r" +
                  " * /ban <user1> <user2> ... - Ban user(s) " +
                  "from your current room\n\r" +
                  " * /unban <user1> <user2> ... - Unban user(s) " +
                  "from your current room \n\r" +
                  " * /delete <name> - Delete a room. " +
                  "Default: current room\n\r" +
                  " * /quit - Disconnect from the server\n\r" +
                  " * Typing backslash with only the first " +
                  "letter of a command works as well\n\r" +
                  " * To use backslash without a command: //\n\r" +
                  "End list")
