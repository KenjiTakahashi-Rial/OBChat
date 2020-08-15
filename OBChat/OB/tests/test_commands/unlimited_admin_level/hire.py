"""
HireTest class container module.
"""

from pytest import mark

from OB.constants import ANON_PREFIX
from OB.models import Admin
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_delete, async_get, async_model_list, async_save, \
    async_try_get

class HireTest(BaseCommandTest):
    """
    Class to test the /hire command function (see OB.commands.unlimited_admin_level.hire).
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
        Tests the /hire command (see OB.commands.unlimited_admin_level.hire).
        """

        # Test anon hiring error
        message = "/hire"
        correct_response = (
            "That's a little outside your pay-grade. Only Unlimited Admins may hire admins. Try to"
            " /apply to be Unlimited."
        )
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test auth user hiring error
        await self.test_isolated(self.auth_users[1], message, correct_response)

        # Test Limited Admin hiring error
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

        # Test owner hiring self error
        message = "/h owner"
        correct_response = (
            "You can't hire yourself. I don't care how good your letter of recommendation is."
        )
        await self.test_isolated(self.owner, message, correct_response)

        # Test Unlimited Admin hiring owner error
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin hiring anonymous user error
        message = f"/h {ANON_PREFIX}0"
        correct_response = (
            f"{ANON_PREFIX}0 hasn't signed up yet. They cannot be trusted with the immense "
            "responsibility that is adminship."
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test owner hiring Unlimited Admin error
        message = "/h unlimited_admin_0"
        correct_response = (
            "unlimited_admin_0 is already an Unlimited Admin. There's nothing left to /hire them"
            " for."
        )
        await self.test_isolated(self.owner, message, correct_response)

        # Test Unlimited Admin hiring Unlimited Admin error
        message = "/h unlimited_admin_1"
        correct_response = (
            "unlimited_admin_1 is already an Unlimited Admin. There's nothing left to /hire them"
            " for."
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin hiring Limited Admin error
        message = "/h limited_admin_0"
        correct_response = (
            "limited_admin_0 is already an Admin. Only the owner may promote them to Unlimited "
            "Admin."
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin hiring authenticated user
        await self.test_success(self.unlimited_admins[0], [self.auth_users[0]])

        # Test Owner hiring authenticated users
        await self.test_success(self.owner, [self.auth_users[0], self.auth_users[1]])

        # Test Owner hiring Limited Admins
        await self.test_success(self.owner, [self.limited_admins[0], self.limited_admins[1]])

    @mark.asyncio
    @mark.django_db()
    async def test_success(self, sender, targets):
        """
        Tests a successful hire through the /hire command.

        Arguments:
            sender (OBUser): The user to send the /hire command.
            targets (list[OBUser]): The users to try to hire.
        """

        # Prepare the message and responses
        message = "/h"
        sender_response = "Hired:\n"
        targets_response = "One or more users have been hired:\n"
        others_response = "One or more users have been hired:\n"

        for user in targets:
            message += f" {user.username}"
            targets_response += f"    {user}\n"
            sender_response += f"    {user}\n"
            others_response += f"    {user}\n"

        sender_response += "Now for the three month evaluation period."
        targets_response += "With great power comes great responsibility."
        others_response += "Drinks on them!"

        # Send the command message
        await self.communicators[sender.username].send(message)
        assert await self.communicators[sender.username].receive() == message

        for user in targets:
            was_already_admin = bool(await async_try_get(Admin, user=user, is_limited=False))

            # Test target response
            assert await self.communicators[user.username].receive() == targets_response

            # Test new adminships
            adminship = await async_get(Admin, user=user, is_limited=not was_already_admin)

            # Undo changes
            if was_already_admin:
                # Make limited again
                adminship.is_limited = True
                await async_save(adminship)
            else:
                # Remove adminship
                await async_delete(adminship)

        # Test sender response
        assert await self.communicators[sender.username].receive() == sender_response

        # Test others response
        occupants = await async_model_list(self.room.occupants)
        for user in occupants:
            if user not in targets and user != sender:
                assert await self.communicators[user.username].receive() == others_response
