"""
LiftCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Ban, OBUser
from OB.strings import StringId
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_save, async_try_get


class LiftCommand(BaseCommand):
    """
    Allow one or more OBConsumers from a group a Room is associated with to rejoin a Room after
    being banned.
    TODO: Viewing a user from inside the Room will show they have been banned before.
    """

    CALLERS = (StringId.LiftCaller, StringId.LiftCallerShort)
    MANUAL = StringId.LiftManual

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticted user
        if self.sender_privilege < Privilege.AuthUser:
            self.sender_receipt += [StringId.AnonLifting]
        # Is authenticated, but not an admin
        elif self.sender_privilege < Privilege.Admin:
            self.sender_receipt += [StringId.NonAdminLifting]
        # Missing target arguments
        elif not self.args:
            self.sender_receipt += [StringId.LiftSyntax]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_arguments().
        """

        for username in self.args:
            arg_user = await async_try_get(OBUser, username=username)
            issuer = None
            issuer_privilege = Privilege.Invalid
            sender_privilege = Privilege.Invalid

            if arg_user:
                arg_ban = await async_try_get(Ban, user=arg_user, room=self.room, is_lifted=False)
                issuer = await async_try_get(OBUser, ban_issued=arg_ban)
                issuer_privilege = await async_get_privilege(issuer, self.room)
                sender_privilege = await async_get_privilege(self.sender, self.room)
            else:
                arg_ban = None

            # Target user is not present or does not have an active ban
            if not arg_user or not arg_ban:
                self.sender_receipt += [StringId.LiftInvalidTarget.format(username)]
            # Target user was banned by someone with higher privilege
            elif issuer_privilege >= sender_privilege and issuer != self.sender:
                self.sender_receipt += [StringId.LiftInsufficientPermission.format(arg_user, issuer)]
            # Is a valid lift
            else:
                self.valid_targets += [(arg_ban, arg_user)]

        return bool(self.valid_targets)

    async def execute_implementation(self):
        """
        Lifts the ban.
        Note that a lifted ban is not deleted, but it is marked as lifted (see OB.models.ban).
        Construct strings to send back to the sender.
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
            [("\n" if self.sender_receipt else "") + StringId.LiftSenderReceiptPreface]
            + lift_message_body
            + [StringId.LiftSenderReceiptNote]
        )
