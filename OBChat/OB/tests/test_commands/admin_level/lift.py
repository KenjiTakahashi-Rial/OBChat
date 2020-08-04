"""
LiftTest class container module.
"""

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import GroupTypes
from OB.models import Ban
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
        correct_response = (
            "You are far from one who can lift bans. Log in and prove yourself an Admin."
        )
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test authenticated user lifting error
        message = "/l"
        correct_response = (
            "A mere mortal like yourself does not have the power to lift bans. Try to /apply to be"
            " an Admin and perhaps you may obtain this power if you are worthy."
        )
        await self.test_isolated(self.auth_users[0], message, correct_response)

        # Test no arguments error
        message = "/l"
        correct_response = "Usage: /lift <user1> <user2> ..."
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test absent target error
        message = "/l auth_user_0_1"
        correct_response = (
            "No user named auth_user_0_1 has been banned from this room. How can one lift that "
            "which has not been banned?"
        )
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Create test ban
        test_ban = await async_save(
            Ban,
            user=self.auth_users[1],
            room=self.room,
            issuer=self.owner
        )

        # Test limited Admin lifting owner-issued ban error
        message = "/l auth_user_1"
        correct_response = (
            f"auth_user_1 was banned by {self.owner}. You cannot lift a ban issued by a user of "
            "equal or higher privilege than yourself. If you REALLY want to lift this ban you can "
            "/elevate to a higher authority."
        )
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test Unlimited Admin lifting owner-issued ban error
        message = "/l auth_user_1"
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test owner lifting ban
        message = "/l auth_user_1"
        correct_response = "\n".join([
            f"Ban lifted:",
            f"   {self.auth_users[1]}",
            f"Fully reformed and ready to integrate into society."
        ])
        await self.communicators["owner"].send(message)
        assert await self.communicators["owner"].receive() == message
        assert await self.communicators["owner"].receive() == correct_response
        self.communicators["auth_user_1"] = await OBCommunicator(
            self.auth_users[1],
            GroupTypes.Room,
            self.room.name
        ).connect()
        await self.communicators["auth_user_1"].disconnect()

        # Create new test ban
        await async_save(
            Ban,
            user=self.auth_users[1],
            room=self.room,
            issuer=self.unlimited_admins[0]
        )

        # Test limited Admin lifting unlimited-admin-issued ban error
        message = "/l auth_user_1"
        correct_response = (
            f"auth_user_1 was banned by {self.unlimited_admins[0]}. You cannot lift a ban issued "
            "by a user of equal or higher privilege than yourself. If you REALLY want to lift this"
            " ban you can /elevate to a higher authority."
        )
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test Unlimited Admin lifting unlimited-admin-issued ban error
        message = "/l auth_user_1"
        await self.test_isolated(self.unlimited_admins[1], message, correct_response)

        # Test Unlimited Admin lifting ban
        message = "/l auth_user_1"
        correct_response = "\n".join([
            f"Ban lifted:",
            f"   {self.auth_users[1]}",
            f"Fully reformed and ready to integrate into society."
        ])
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)
