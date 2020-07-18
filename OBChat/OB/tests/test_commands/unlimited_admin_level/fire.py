"""
Description:
    FireTest class container module.
"""

from pytest import mark

from OB.tests.test_commands.base import BaseCommandTest

class FireTest(BaseCommandTest):
    """
    Description:
        Class to test the /fire command function (see OB.commands.unlimited_admin_level.fire).
    """

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
            Tests the /fire command (see OB.commands.unlimited_admin_level.fire).
        """

        # Test anon firing error
        message = "/fire"
        correct_response = (
            "That's a little outside your pay-grade. Only Unlimited Admins may fire admins. Try to"
            " /apply to be Unlimited."
        )
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test auth user firing error
        await self.test_isolated(self.auth_users[0], message, correct_response)

        # Test Limited Admin hiring error
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test no arguments error
        correct_response = "Usage: /fire <user1> <user2> ..."
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test invalid target error
        message = "/f nobody"
        correct_response = f"nobody does not exist. You can't fire a ghost... can you?"
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test owner firing self
        message = "/f owner"
        correct_response = (
            "You can't fire yourself. I don't care how bad your performance reviews are."
        )
        await self.test_isolated(self.owner, message, correct_response)

        # Test Unlimited Admin firing owner error
        correct_response = ("That's the owner. You know, your BOSS. Nice try.")
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin firing non-Admin error
        message = "/f auth_user_0"
        correct_response = (
            "auth_user_0 is just a regular ol' user, so you can't fire them. You can /kick or /ban"
            " them if you want."
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin firing Unlmiited Admin error
        message = "/f unlimited_admin_1"
        correct_response = (
            "unlimited_admin_1 is an Unlimited Admin, so you can't fire them. Please direct all "
            "complaints to your local room owner, I'm sure they'll love some more paperwork to "
            "do..."
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)
