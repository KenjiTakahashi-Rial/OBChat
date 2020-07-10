"""
Class to test the /apply command function (see OB.commands.auth_user_level.apply).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_filter, async_get

class ApplyTest(BaseCommandTest):
    def __init__(self):
        """
        Description:
            Declares the instance variables that be used for testing, includes communicators and
            database objects.
        """

        super().__init__(unlimited_admins=2, limited_admins=2, auth_users=2, anon_users=2)

    @mark.asyncio
    @mark.django_db()
    async def tests(self):
        """
        Description:
            Tests the /apply command (see OB.commands.user_level.apply).
        """

        # Test unauthenticated user error
        message = "/apply"
        correct_response = (
            "You can't get hired looking like that! Clean yourself up and make an account first."
        )
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test unlimited admin error
        correct_response = "You're already a big shot! There's nothing left to apply to."
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test owner error
        await self.test_isolated(self.owner, message, correct_response)

        # Test authenticated user
        await self.test_success(self.auth_users[0])

        # Test limited admin
        await self.test_success(self.limited_admins[0], "How do into unlimited admin?")

    @mark.asyncio
    @mark.django_db()
    async def test_success(self, sender, message=""):
        """
        Description:
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
        user_suffix = " [admin]" if sender_privilege == Privilege.Admin else ""
        position_prefix = "Unlimited " if sender_privilege == Privilege.Admin else ""
        message = message if message else None

        application = "\n".join([
            f"Application Received",
            f"   User: {sender}{user_suffix}",
            f"   Position: {position_prefix}Admin",
            f"   Message: {message}",
            f"To hire this user, use /hire."
        ])

        receipt = (
            "Your application was received. Hopefully the response doesn't start with: \"After "
            "careful consideration...\""
        )

        # Gather recipients
        if sender_privilege == Privilege.Admin:
            recipients = [self.owner]
        else:
            recipients = []
            for adminship in await async_filter(Admin, room=self.room, is_limited=False):
                recipients += [await async_get(OBUser, adminship=adminship)]

        # Test recipient response
        for user in recipients:
            assert await self.communicators[user.username].receive() == application

        # Test sender response
        assert await self.communicators[sender.username].receive() == f"/apply{command}"
        assert await self.communicators[sender.username].receive() == receipt
