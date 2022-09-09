"""
ApplyTest class container module.
"""

from pytest import mark

from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.strings import StringId
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_filter, async_get


class ApplyTest(BaseCommandTest):
    """
    Class to test the /apply command function (see OB.commands.auth_user_level.apply).
    """

    def __init__(self):
        """
        Declares the instance variables that be used for testing, includes communicators and
        database objects.
        """

        super().__init__(unlimited_admins=2, limited_admins=2, auth_users=2, anon_users=2)

    @mark.asyncio
    @mark.django_db()
    async def tests(self):
        """
        Tests the /apply command (see OB.commands.user_level.apply).
        """

        # Test unauthenticated user error
        message = "/apply"
        correct_response = StringId.AnonApplying
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test Unlimited Admin error
        correct_response = StringId.UnlimitedAdminApplying
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test owner error
        await self.test_isolated(self.owner, message, correct_response)

        # Test authenticated user
        await self.test_success(self.auth_users[0])

        # Test limited admin
        await self.test_success(self.limited_admins[0], "How do into Unlimited Admin?")

    @mark.asyncio
    @mark.django_db()
    async def test_success(self, sender, message=""):
        """
        Tests a successful application through the /apply command.

        Arguments:
            sender (OBUser): The user to send the /apply command.
            message (string): The accompanying message for the application.
        """

        sender_privilege = await async_get_privilege(sender, self.room)

        # Send the command
        command = f" {message}" if message else ""
        await self.communicators[sender.username].send(f"/apply{command}")

        # Prepare the responses
        user_suffix = StringId.AdminSuffix if sender_privilege == Privilege.Admin else ""
        position_prefix = StringId.Unlimited if sender_privilege == Privilege.Admin else ""
        message = message if message else None

        application_body = [
            f"   {StringId.User} {sender}{user_suffix}",
            f"   {StringId.Position} {position_prefix}{StringId.Admin}",
            f"   {StringId.Message} {message}",
        ]

        sender_receipt = "\n".join(
            [StringId.ApplySenderReceiptPreface] + application_body + [StringId.ApplySenderReceiptNote]
        )

        targets_notification = "\n".join(
            [StringId.ApplyTargetsNotificationPreface] + application_body + [StringId.ApplyTargetsNotificationNote]
        )

        # Gather recipients
        recipients = []

        if sender_privilege < Privilege.Admin:
            for adminship in await async_filter(Admin, room=self.room, is_limited=False):
                recipients += [await async_get(OBUser, adminship=adminship)]

        recipients += [self.owner]

        # Test recipient response
        for user in recipients:
            assert await self.communicators[user.username].receive() == targets_notification

        # Test sender response
        assert await self.communicators[sender.username].receive() == f"/apply{command}"
        assert await self.communicators[sender.username].receive() == sender_receipt
