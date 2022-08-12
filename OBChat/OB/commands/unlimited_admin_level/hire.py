"""
HireCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.strings import StringId
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_save, async_try_get


class HireCommand(BaseCommand):
    """
    Increases the privilege of an Admin or authenticated user by 1.
    Admins have their adminships un-limited.
    Authenticated users receive a limited adminship.
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is not an Unlimited Admin
        if self.sender_privilege < Privilege.UnlimitedAdmin:
            self.sender_receipt = [StringId.NonUnlimitedAdminHiring]
        # Missing target arguments
        elif len(self.args) == 0:
            self.sender_receipt = [StringId.HireSyntax]

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
                self.sender_receipt += [StringId.HireInvalidTarget.format(username)]
            # Target user is the sender, themself
            elif arg_user == self.sender:
                self.sender_receipt += [StringId.HireSelf]
            # Target user is the owner
            elif arg_privilege == Privilege.Owner:
                self.sender_receipt += [StringId.TargetOwner]
            # Target user is an anonymous/unauthenticated
            elif not arg_user.is_authenticated or arg_user.is_anon:
                self.sender_receipt += [StringId.HireAnon.format(arg_user)]
            # Target may not be promoted by sender
            elif arg_admin and self.sender_privilege < Privilege.Owner:
                self.sender_receipt += [
                    StringId.HireInsufficientPrivilege.format(arg_user)
                ]
            # Target user is an Unlimited Admin
            elif arg_admin and not arg_admin.is_limited:
                self.sender_receipt += [StringId.HireUnlimitedAdmin.format(arg_user)]
            # Target user is a valid hire
            else:
                self.valid_targets += [(arg_user, arg_admin)]

        return bool(self.valid_targets)

    async def execute_implementation(self):
        """
        Add adminships for targets who are not already an Admin.
        Un-limit the adminships for targets who are already an Admin.
        Constructs strings to send back to the sender and to the other occupants of the room.
        The sender receipt includes per-argument error messages.
        """

        hire_message_body = []

        for hired_user, target_adminship in self.valid_targets:
            if target_adminship and self.sender_privilege == Privilege.Owner:
                # Make the Admin unlimited
                target_adminship.is_limited = False
                await async_save(target_adminship)
            else:
                # Make an adminship for the user
                await async_save(
                    Admin, user=hired_user, room=self.room, issuer=self.sender
                )

            hire_message_body += [f"    {hired_user}"]

        self.sender_receipt += (
            # Add an extra newline to separate argument error messages from fire receipt
            [("\n" if self.sender_receipt else "") + StringId.HireSenderReceiptPreface]
            + hire_message_body
            + [StringId.HireSenderReceiptNote]
        )

        self.occupants_notification += (
            [StringId.HireOccupantsNotificationPreface]
            + hire_message_body
            + [StringId.HireOccupantsNotificationNote]
        )

        self.targets_notification += (
            [StringId.HireOccupantsNotificationPreface]
            + hire_message_body
            + [StringId.HireTargetsNotificationNote]
        )

    async def send_responses(self):
        """
        Change the valid_targets list to be a list of OBUsers instead of a list of tuples.
        """

        self.valid_targets = [
            hired_user for hired_user, existing_adminship in self.valid_targets
        ]
        await super().send_responses()
