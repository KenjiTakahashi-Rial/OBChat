"""
Class to test the /hire command function (see OB.commands.unlimited_admin_level.hire).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.constants import ANON_PREFIX
from OB.models import Admin
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_get, async_model_list, async_try_get

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
            " /apply to be Unlimited."
        )
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test auth user hiring error
        await self.test_isolated(self.auth_users[1], message, correct_response)

        # Test limited Admin hiring error
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

        # Test hiring self error
        message = "/h owner"
        correct_response = (
            "You can't hire yourself. I don't care how good your letter of recommendation is."
        )
        await self.test_isolated(self.owner, message, correct_response)

        # Test hiring owner error
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test hiring anonymous user error
        message = f"/h {ANON_PREFIX}0"
        correct_response = (
            f"{ANON_PREFIX}0 hasn't signed up yet. They cannot be trusted with the immense "
            "responsibility that is adminship."
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test hiring Unlimited Admin error
        message = "/h unlimited_admin_0"
        correct_response = (
            "unlimited_admin_0 is already an Unlimited Admin. There's nothing left to /hire them"
            " for."
        )
        await self.test_isolated(self.owner, message, correct_response)

        # Test Unlimited Admin hiring Limited Admin error
        message = "/h limited_admin_0"
        correct_response = (
            "limited_admin_0 is already an Admin. Only the owner may promote them to Unlimited "
            "Admin."
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin hiring authenticated user
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

    @mark.asyncio
    @mark.django_db()
    async def test_success(self, sender, targets):
        """
        Description:
            Tests a successful hire through the /hire command.
        Arguments:
            sender (OBUser): The user to send the /hire command.
            targets (list[OBUser]): The users to try to hire.
        """

        # Prepare the message
        message = "/h"
        for user in targets:
            message += f" {user.username}"

        # Send the command message
        await self.communicators[sender.username].send(message)
        assert await self.communicators[sender.username].receive() == message

        for user in targets:
            admin_prefix = "Unlimited " if await async_try_get(Admin, user=user) else ""

            # Test target response
            target_response = (
                f"With great power comes great responsibility. You were promoted to {admin_prefix}"
                f"Admin in {self.room.name}!"
            )
            assert await self.communicators[user.username].receive() == target_response

            # Test sender response
            sender_response = (
                f"Promoted {user.username} to {admin_prefix}Admin in {self.room.name}. Keep an "
                "eye on them."
            )
            assert await self.communicators[sender.username].receive() == sender_response

            # Test others response
            others_response = (
                f"{user.username} was promoted to {admin_prefix}Admin. Drinks on them!"
            )
            occupants = await async_model_list(self.room.occupants)
            for occupying_user in occupants:
                if occupying_user != sender and occupying_user not in targets:
                    assert (
                        await self.communicators[occupying_user.username].receive()
                        == others_response
                    )

            # Test new adminships
            await async_get(Admin, user=user, is_limited=bool(not admin_prefix))
