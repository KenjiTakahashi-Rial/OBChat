"""
Class to test the /hire command function (see OB.commands.unlimited_admin_level.hire).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.tests.test_commands.base import BaseCommandTest

class HireTest(BaseCommandTest):
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
            Tests the /hire command (see OB.commands.unlimited_admin_level.hire).
        """

        # Test anon hiring error
        message = "/hire"
        correct_response = (
            "That's a little outside your pay-grade. Only Unlimited Admins may hire admins. Try to"
            " /apply to be unlimited."
        )
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test auth user hiring error
        await self.test_isolated(self.auth_users[1], message, correct_response)

        # Test limited admin hiring error
        await self.test_isolated(self.limited_admins[1], message, correct_response)

        # Test no arguments error
        correct_response = "Usage: /hire <user1> <user2> ..."
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test invalid target error
        message = "/h nobody"
        correct_response = (
            f"nobody does not exist. Your imaginary friend needs an account before they can be"
            " an Admin."
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)
