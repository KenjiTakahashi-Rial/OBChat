"""
LiftTest class container module.
"""

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import GroupTypes
from OB.models import Ban
from OB.strings import StringId
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_save


class LiftTest(BaseCommandTest):
    """
    Class to test the /lift command function (see OB.commands.admin_level.lift).
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
        Tests the /lift command (see OB.commands.user_level.lift).
        """

        # Test unauthenticated user lifting error
        message = "/lift"
        correct_response = StringId.AnonLifting
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test authenticated user lifting error
        message = "/l"
        correct_response = StringId.NonAdminLifting
        await self.test_isolated(self.auth_users[0], message, correct_response)

        # Test no arguments error
        message = "/l"
        correct_response = StringId.LiftSyntax
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test absent target error
        message = "/l auth_user_0_1"
        correct_response = StringId.LiftInvalidTarget.format("auth_user_0_1")
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Create test ban
        await async_save(Ban, user=self.auth_users[1], room=self.room, issuer=self.owner)

        # Test limited Admin lifting owner-issued ban error
        message = "/l auth_user_1"
        correct_response = StringId.LiftInsufficientPermission.format(self.auth_users[1], self.owner)
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test Unlimited Admin lifting owner-issued ban error
        message = "/l auth_user_1"
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test owner lifting ban
        message = "/l auth_user_1"
        correct_response = "\n".join(
            [
                StringId.LiftSenderReceiptPreface,
                f"   {self.auth_users[1]}",
                StringId.LiftSenderReceiptNote,
            ]
        )
        await self.communicators["owner"].send(message)
        assert await self.communicators["owner"].receive() == message
        assert await self.communicators["owner"].receive() == correct_response
        self.communicators["auth_user_1"] = await OBCommunicator(
            self.auth_users[1], GroupTypes.Room, self.room.name
        ).connect()
        await self.communicators["auth_user_1"].disconnect()

        # Create new test ban
        await async_save(
            Ban,
            user=self.auth_users[1],
            room=self.room,
            issuer=self.unlimited_admins[0],
        )

        # Test limited Admin lifting unlimited-admin-issued ban error
        message = "/l auth_user_1"
        correct_response = StringId.LiftInsufficientPermission.format(self.auth_users[1], self.unlimited_admins[0])
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test Unlimited Admin lifting unlimited-admin-issued ban error
        message = "/l auth_user_1"
        await self.test_isolated(self.unlimited_admins[1], message, correct_response)

        # Test Unlimited Admin lifting ban
        message = "/l auth_user_1"
        correct_response = "\n".join(
            [
                StringId.LiftSenderReceiptPreface,
                f"   {self.auth_users[1]}",
                StringId.LiftSenderReceiptNote,
            ]
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

    async def test_success(self, sender, targets):
        """
        Tests a successful kick through the /kick command.

        Arguments:
            sender (OBUser): The user to send the /kick command.
            targets (list[OBUser]): The users to try to kick.
        """

        # TODO: Implement this
