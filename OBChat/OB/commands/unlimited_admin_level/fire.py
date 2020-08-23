"""
FireCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.strings import StringId
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_save, async_try_get

class FireCommand(BaseCommand):
    """
    Reduces the privilege of an Admin or Unlimited Admin user by 1.
    Admins have their adminships deleted.
    Unlimited Admins have their adminships limited.
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is not an Unlimited Admin
        if self.sender_privilege < Privilege.UnlimitedAdmin:
            self.sender_receipt = [StringId.NonUnlimitedAdminFiring]
        # Missing target arguments
        elif len(self.args) == 0:
            self.sender_receipt = [StringId.FireSyntax]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_arguments().
        """

        for username in self.args:
            arg_user = await async_try_get(OBUser, username=username)

            if arg_user:
                arg_privilege = await async_get_privilege(arg_user, self.room)
                arg_admin = await async_try_get(Admin, user=arg_user, room=self.room)

            # Target user does not exist
            if not arg_user:
                self.sender_receipt += [StringId.FireUserNotPresent.format(username)]
            # Target user is the sender, themself
            elif arg_user == self.sender:
                self.sender_receipt += [StringId.FireSelf]
            # Target user is the owner
            elif arg_privilege == Privilege.Owner:
                self.sender_receipt += [StringId.TargetOwner]
            # Target user is not an Admin
            elif not arg_admin:
                self.sender_receipt += [StringId.FireNonAdmin.format(arg_user)]
            # Target user has higher privilege than sender
            elif not arg_admin.is_limited and self.sender_privilege < Privilege.Owner:
                self.sender_receipt += [StringId.FirePeer.format(arg_user)]
            # Is a valid fire
            else:
                self.valid_targets += [{"user": arg_user, "adminship": arg_admin}]

            return bool(self.valid_targets)

    async def execute_implementation(self):
        """
        Removes adminships of targets.
        Constructs strings to send back to the sender and other occupants of the room.
        The sender receipt includes per-argument error messages.
        """

        fire_message_body = []

        for fired_user in self.valid_targets:
            # Remove the adminship if they were a normal Admin
            if fired_user["adminship"].is_limited:
                await async_delete(fired_user["adminship"])
            # Limit the adminship if they were an Unlimited Admin
            else:
                fired_user["adminship"].is_limited = True
                await async_save(fired_user["adminship"])

            fire_message_body += [f"    {fired_user}"]

        self.sender_receipt += (
            # Add an extra newline to separate argument error messages from fire receipt
            [("\n" if self.sender_receipt else "") + StringId.FireSenderReceiptPreface] +
            fire_message_body +
            [StringId.FireSenderReceiptNote]
        )

        self.occupants_notification += (
            [StringId.FireOccupantsNotificationPreface] +
            fire_message_body +
            [StringId.FireOccupantsNotificationNote]
        )

        self.targets_notification += (
            [StringId.FireOccupantsNotificationPreface] +
            fire_message_body +
            [StringId.FireTargetsNotificationNote]
        )
