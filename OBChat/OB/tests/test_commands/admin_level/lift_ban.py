"""
Class to test the /lift command function (see OB.commands.admin_level.lift()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import Ban
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_save

class LiftTest(BaseCommandTest):
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
            Tests the /lift command (see OB.commands.user_level.lift_ban()).
        """

        # Test unauthenticated user lifting error
        message = "/lift"
        correct_response = (
            "You are far from one who can lift bans. Log in and prove yourself an admin."
        )
        await self.communicators[f"{ANON_PREFIX}0"].send(message)
        assert await self.communicators[f"{ANON_PREFIX}0"].receive() == message
        assert await self.communicators[f"{ANON_PREFIX}0"].receive() == correct_response

        # Test authenticated user lifting error
        message = "/l"
        correct_response = (
            "A mere mortal like yourself does not have the power to lift bans. Try to /apply to be"
            " an admin and perhaps you may obtain this power if you are worthy."
        )
        await self.communicators["auth_user_0"].send(message)
        assert await self.communicators["auth_user_0"].receive() == message
        assert await self.communicators["auth_user_0"].receive() == correct_response

        # Test no arguments error
        message = "/l"
        correct_response = "Usage: /lift <user1> <user2> ..."
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test absent target error
        message = "/l auth_user_0_1"
        correct_response = (
            "No user named auth_user_0_1 has been banned from this room. How can one lift that "
            "which has not been banned?"
        )
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Create test ban
        await async_save(
            Ban,
            user=self.auth_users[1],
            room=self.room,
            issuer=self.owner
        )

        # Test limited admin lifting owner-issued ban error
        message = "/l auth_user_1"
        correct_response = (
            f"auth_user_1 was banned by {self.owner}. You cannot lift a ban issued by a user of "
            "equal or higher privilege than yourself. If you REALLY want to lift this ban you can "
            "/elevate to a higher authority."
        )
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test unlimited admin lifting owner-issued ban error
        message = "/l auth_user_1"
        await self.communicators["unlimited_admin_0"].send(message)
        assert await self.communicators["unlimited_admin_0"].receive() == message
        assert await self.communicators["unlimited_admin_0"].receive() == correct_response

        # Test owner lifting ban
        message = "/l auth_user_1"
        correct_response = "\n".join([
            "Ban lifted:",
            f"   {self.auth_users[1]}",
            "Fully reformed and ready to integrate into society."
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

        # Create test ban
        await async_save(
            Ban,
            user=self.auth_users[1],
            room=self.room,
            issuer=self.unlimited_admins[0]
        )

        # Test limited admin lifting unlimited-admin-issued ban error
        message = "/l auth_user_1"
        correct_response = (
            f"auth_user_1 was banned by {self.unlimited_admins[0]}. You cannot lift a ban issued by a "
            "user of equal or higher privilege than yourself. If you REALLY want to lift this ban "
            "you can /elevate to a higher authority."
        )
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test unlimited admin lifting unlimited-admin-issued ban error
        message = "/l auth_user_1"
        await self.communicators["unlimited_admin_1"].send(message)
        assert await self.communicators["unlimited_admin_1"].receive() == message
        assert await self.communicators["unlimited_admin_1"].receive() == correct_response

        # Test unlimited admin lifting ban
        message = "/l auth_user_1"
        correct_response = "\n".join([
            "Ban lifted:",
            f"   {self.auth_users[1]}",
            "Fully reformed and ready to integrate into society."
        ])
        await self.communicators["unlimited_admin_0"].send(message)
        assert await self.communicators["unlimited_admin_0"].receive() == message
        assert await self.communicators["unlimited_admin_0"].receive() == correct_response
