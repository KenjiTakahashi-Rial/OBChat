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

    def __init__(self, args, sender, room):
        """
        See BaseCommand.__init__().
        """

        super().__init__(args, sender, room)
        self.valid_bans = []

    async def execute(self):
        """
        The main implementation of the /ban command.
        """

        # Remove duplicates
        self.args = list(dict.fromkeys(self.args))

        # Check for initial errors
        if not await self.check_initial_errors():
            pass
        # Check the validity of the arguments
        elif not await self.check_arguments():
            pass
        # Execute the bans
        else:
            await self.execute_bans()

        await self.send_responses()

    async def check_initial_errors(self):
        """
        Check for initial errors such as lack of privilege or invalid syntax.
        If there are any errors, send them back to the issuing user.

        Return values:
            boolean: True if there were no initial errors.
        """

        self.sender_privilege = await async_get_privilege(self.sender, self.room)

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
        Check each argument for errors such as self-targeting or targeting a user of higher
        privilege.

        Return values:
            boolean: True if any of the arguments are a valid ban.
        """

        for username in self.args:
            arg_user = await async_try_get(OBUser, username=username)
            arg_privilege = None if not arg_user else await async_get_privilege(arg_user, self.room)

            if not arg_user:
                # Target user does not exist
                self.sender_receipt += [
                    f"Nobody named {username} in this room. Are you seeing things?"
                ]
            elif arg_user == self.sender:
                # Target user is the sender, themself
                self.sender_receipt += [
                    f"You can't ban yourself. Just leave the room. Or put yourself on time-out."
                ]
            elif arg_privilege == Privilege.Owner:
                # Target user is the owner
                self.sender_receipt += [f"That's the owner. You know, your BOSS. Nice try."]
            elif arg_privilege >= self.sender_privilege:
                # Target user has Privilege greater than or equal to the sender
                job_title = "Admin"

                if arg_privilege == await async_get_privilege(self.sender, self.room):
                    job_title += " just like you"

                if arg_privilege == Privilege.UnlimitedAdmin:
                    job_title = "Unlimited " + job_title

                self.sender_receipt += [
                    f"{arg_user} is an {job_title}, so you can't ban them. Feel free to "
                    "/elevate your complaints to someone who has more authority."
                ]
            else:
                # Target user is a valid ban
                self.valid_bans += [arg_user]

        return bool(self.valid_bans)

    async def execute_bans(self):
        """
        Kick and ban users from the room.
        Constructs strings to send back to the sender and to the other occupants of the room.
        The sender receipt includes per-argument error messages.
        """

        # Prepend the argument error messages to the sender's receipt
        self.sender_receipt += [("\n" if self.sender_receipt else "") + "Banned:"]
        self.occupants_notification = ["One or more users have been banned:"]

        for banned_user in self.valid_bans:
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
            self.sender_receipt += [f"   {banned_user}"]
            self.occupants_notification += [f"   {banned_user}"]

        self.sender_receipt += ["That'll show them."]
        self.occupants_notification += ["Let this be a lesson to you all."]
