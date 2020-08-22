"""
ApplyCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.strings import StringId
from OB.utilities.database import async_filter, async_get, async_get_owner

class ApplyCommand(BaseCommand):
    """
    Sends a request for a user to be hired as an Admin or promoted to Unlimited Admin.
    The request is visible by all users with hiring privileges of the room.
    Optionally includes a message.
    """

    def __init__(self, args, sender, room):
        """
        Arguments of /apply are a message, so do not remove duplicates.
        """

        super().__init__(args, sender, room)
        self.remove_duplicates = False

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticated user
        if self.sender_privilege < Privilege.AuthUser:
            self.sender_receipt += [StringId.AnonApplying]
        # Is already an Unlimited Admin
        elif self.sender_privilege >= Privilege.UnlimitedAdmin:
            self.sender_receipt += [StringId.UnlimitedAdminApplying]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        Arguments can only be a message to send along with the application, so they do not need to
        be checked for errors like with other commands.
        """

        return True

    async def execute_implementation(self):
        """
        Gathers recipients for the application.
        Constructs strings to send back to the sender and to those who may hire them.
        """

        # Gather recipients
        if self.sender_privilege < Privilege.Admin:
            unlimited_admins = await async_filter(
                Admin,
                room=self.room,
                is_limited=False
            )

            for adminship in unlimited_admins:
                self.valid_targets += [await async_get(OBUser, adminship=adminship)]

        self.valid_targets += [await async_get_owner(self.room)]

        # Construct strings
        user_suffix = StringId.AdminSuffix if self.sender_privilege == Privilege.Admin else ""
        position_prefix = StringId.Unlimited if self.sender_privilege == Privilege.Admin else ""
        application_message = " ".join(self.args) if self.args else None

        application_body = [
            f"   {StringId.User} {self.sender}{user_suffix}",
            f"   {StringId.Position} {position_prefix}{StringId.Admin}",
            f"   {StringId.Message} {application_message}"
        ]

        self.sender_receipt += (
            # Add an exra newline to separate argument error messages from ban receipt
            [("\n" if self.sender_receipt else "") + StringId.ApplySenderReceiptPreface] +
            application_body +
            [StringId.ApplySenderReceiptNote]
        )

        self.targets_notification += (
            [StringId.ApplyTargetsNotificationPreface] +
            application_body +
            [StringId.ApplyTargetsNotificationNote]
        )
