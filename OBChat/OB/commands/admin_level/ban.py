"""
BanCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Ban, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_save, async_try_get
from OB.utilities.event import send_room_event

class BanCommand(BaseCommand):
    """
    Remove one or more OBConsumers from the group a Room is associated with and do not allow them
    to rejoin the group. Bans may be lifted (see lift()).
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticated user
        if self.sender_privilege < Privilege.AuthUser:
            self.sender_receipt = [
                "You're not even logged in! Try making an account first, then we can talk about "
                "banning people."
            ]
        # Is authenticated, but not an admin
        elif self.sender_privilege < Privilege.Admin:
            self.sender_receipt = [
                "That's a little outside your pay-grade. Only admins may ban users. Try to /apply "
                "to be an Admin."
            ]
        # Missing target arguments
        elif not self.args:
            self.sender_receipt = ["Usage: /ban <user1> <user2> ..."]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_arguments().
        """

        for username in self.args:
            arg_user = await async_try_get(OBUser, username=username)

            if arg_user:
                arg_privilege = await async_get_privilege(arg_user, self.room)
                arg_ban = await async_try_get(Ban, user=arg_user, room=self.room, is_lifted=False)

            # Target user does not exist
            if not arg_user:
                self.sender_receipt += [
                    f"Nobody named {username} in this room. Are you seeing things?"
                ]
            # Target user is the sender, themself
            elif arg_user == self.sender:
                self.sender_receipt += [
                    "You can't ban yourself. Just leave the room. Or put yourself on time-out."
                ]
            # Target user is the owner
            elif arg_privilege == Privilege.Owner:
                self.sender_receipt += ["That's the owner. You know, your BOSS. Nice try."]
            # Target user is already banned
            elif arg_ban:
                self.sender_receipt += ["That user is already banned. How unoriginal of you."]
            # Target user has Privilege greater than or equal to the sender
            elif arg_privilege >= self.sender_privilege:
                job_title = "Admin"

                if arg_privilege == await async_get_privilege(self.sender, self.room):
                    job_title += " just like you"

                if arg_privilege == Privilege.UnlimitedAdmin:
                    job_title = "Unlimited " + job_title

                self.sender_receipt += [
                    f"{arg_user} is an {job_title}, so you can't ban them. Feel free to "
                    "/elevate your complaints to someone who has more authority."
                ]
            # Target user is a valid ban
            else:
                self.valid_targets += [arg_user]

        return bool(self.valid_targets)

    async def execute_implementation(self):
        """
        Kick and ban users from the room.
        Constructs strings to send back to the sender and to the other occupants of the room.
        The sender receipt includes per-argument error messages.
        """

        ban_message_body = []

        for banned_user in self.valid_targets:
            # Save the ban to the database
            await async_save(
                Ban,
                user=banned_user,
                room=self.room,
                issuer=self.sender
            )

            # Kick the user
            kick_event = {
                "type": "kick",
                "target_id": banned_user.id
            }
            await send_room_event(self.room.id, kick_event)

            # Add the user's name to the sender receipt and occupants notification
            ban_message_body += [f"   {banned_user}"]

        self.sender_receipt += (
            # Add an exra newline to separate argument error messages from ban receipt
            [("\n" if self.sender_receipt else "") + "Banned:"] +
            ban_message_body +
            ["That'll show them."]
        )
        self.occupants_notification += (
            ["One or more users have been banned:"] +
            ban_message_body +
            ["Let this be a lesson to you all."]
        )
