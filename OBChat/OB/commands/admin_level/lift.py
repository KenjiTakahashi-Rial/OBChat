"""
LiftCommand class container module
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Ban, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_save, async_try_get
from OB.utilities.event import send_system_room_message

class LiftCommand(BaseCommand):
    """
    Allow one or more OBConsumers from a group a Room is associated with to rejoin a Room after
    being banned.
    TODO: Viewing a user from inside the Room will show they have been banned before.
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticted user
        if self.sender_privilege < Privilege.AuthUser:
            self.sender_receipt += [
                "You are far from one who can lift bans. Log in and prove yourself an Admin."
            ]
        # Is authenticated, but not an admin
        elif self.sender_privilege < Privilege.Admin:
            self.sender_receipt += [
                "A mere mortal like yourself does not have the power to lift bans. Try to /apply "
                "to be an Admin and perhaps you may obtain this power if you are worthy."
            ]
        # Missing target arguments
        elif not self.args:
            self.sender_receipt += ["Usage: /lift <user1> <user2> ..."]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_initial_errors().
        """

        for username in self.args:
            arg_user = await async_try_get(OBUser, username=username)

            if arg_user:
                arg_ban = await async_try_get(Ban, user=arg_user, room=self.room)
                issuer = await async_try_get(OBUser, ban_issued=arg_ban)
                issuer_privilege = await async_get_privilege(issuer, self.room)
                sender_privilege = await async_get_privilege(self.sender, self.room)
            else:
                arg_ban = None

            # Target user is not present or does not have an active ban
            if not arg_user or not arg_ban:
                self.sender_receipt += [
                    f"No user named {username} has been banned from this room. How can "
                    "one lift that which has not been banned?"
                ]
            # Target user was banned by someone with higher privilege
            elif issuer_privilege >= sender_privilege and issuer != self.sender:
                self.sender_receipt += [
                    f"{username} was banned by {issuer}. You cannot lift a ban issued by a "
                    "user of equal or higher privilege than yourself. If you REALLY want to lift "
                    "this ban you can /elevate to a higher authority."
                ]
            else:
                self.valid_targets += [(arg_ban, arg_user)]

        return bool(self.valid_targets)

    async def execute_implementation(self):
        """
        Lifts the ban.
        Note that a lifted ban is not deleted, but it is marked as lifted (see OB.models.ban).
        Constructs strings to send back to the sender.
        The sender receipt includes per-argument error messages.
        """

        lift_message_body = []

        for lifted_ban, lifted_user in self.valid_targets:
            # Mark the ban as lifted
            lifted_ban.is_lifted = True
            await async_save(lifted_ban)

            lift_message_body += [f"   {lifted_user}"]

        self.sender_receipt += (
            # Add an extra newline to separate argument error messages from lift receipt
            [("\n" if self.sender_receipt else "") + "Ban lifted:"] +
            lift_message_body +
            ["Fully reformed and ready to integrate into society."]
        )
