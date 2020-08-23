"""
FireTest class container module.
"""

from pytest import mark

from OB.strings import StringId
from OB.tests.test_commands.base import BaseCommandTest

class FireTest(BaseCommandTest):
    """
    Class to test the /fire command function (see OB.commands.unlimited_admin_level.fire).
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
        Tests the /fire command (see OB.commands.unlimited_admin_level.fire).
        """

        # Test anon firing error
        message = "/fire"
        correct_response = StringId.NonUnlimitedAdminFiring
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test auth user firing error
        await self.test_isolated(self.auth_users[0], message, correct_response)

        # Test Limited Admin hiring error
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test no arguments error
        correct_response = StringId.FireSyntax
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test invalid target error
        message = "/f nobody"
        correct_response = StringId.FireUserNotPresent.format("nobody")
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test owner firing self
        message = "/f owner"
        correct_response = StringId.FireSelf
        await self.test_isolated(self.owner, message, correct_response)

        # Test Unlimited Admin firing owner error
        correct_response = StringId.TargetOwner
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin firing non-Admin error
        message = "/f auth_user_0"
        correct_response = StringId.FireNonAdmin.format(self.auth_users[0])
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin firing Unlmiited Admin error
        message = "/f unlimited_admin_1"
        correct_response = StringId.FirePeer.format(self.unlimited_admins[1])
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

