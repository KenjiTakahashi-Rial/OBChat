"""
ApplyTest class container module.
"""

from pytest import mark

from OB.constants import Privilege
from OB.models import Admin, OBUser
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
        correct_response = (
            "You can't get hired looking like that! Clean yourself up and make an account first."
        )
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test Unlimited Admin error
        correct_response = (
            "You're already a big shot Unlimited Admin! There's nothing left to apply to."
        )
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
        user_suffix = " [Admin]" if sender_privilege == Privilege.Admin else ""
        position_prefix = "Unlimited " if sender_privilege == Privilege.Admin else ""
        message = message if message else None

        application_body = [
            f"   User: {sender}{user_suffix}",
            f"   Position: {position_prefix}Admin",
            f"   Message: {message}"
        ]

        sender_receipt = "\n".join(
            # Add an exra newline to separate argument error messages from ban receipt
            ["Application sent:"] +
            application_body +
            ["Hopefully the response doesn't start with: \"After careful consideration...\""]
        )

        targets_notification = "\n".join(
            ["Application Received"] +
            application_body +
            ["To hire this user, use /hire."]
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
