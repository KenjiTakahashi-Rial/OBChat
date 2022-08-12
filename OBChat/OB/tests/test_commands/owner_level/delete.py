"""
DeleteTest class container module.
"""

from pytest import mark

from OB.models import Admin, Ban, Message, Room
from OB.strings import StringId
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_filter, async_save, async_try_get


class DeleteTest(BaseCommandTest):
    """
    Class to test the /delete command function (see OB.commands.owner_level.delete).
    """

    def __init__(self):
        """
        Declares the instance variables that be used for testing, includes communicators and
        database objects.
        """

        super().__init__(
            unlimited_admins=2, limited_admins=2, auth_users=2, anon_users=2
        )

    @mark.asyncio
    @mark.django_db()
    async def tests(self):
        """
        Tests the /delete command (see OB.commands.owner_level.delete).
        """

        # Test anonymous user deleting error
        message = "/d"
        correct_response = StringId.NonOwnerDeleting
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test authenticated user deleting error
        await self.test_isolated(self.auth_users[0], message, correct_response)

        # Test Limited Admin user deleting error
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test Unlimited Admin user deleting error
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test no arguments error
        correct_response = StringId.DeleteSyntax
        await self.test_isolated(self.owner, message, correct_response)

        # Test too many arguments error
        message = "/d arg0 arg1 arg2"
        await self.test_isolated(self.owner, message, correct_response)

        # Test incorrect arguments error
        message = "/d roomname username"
        await self.test_isolated(self.owner, message, correct_response)

        # Create test data
        await async_save(
            Ban, user=self.auth_users[0], room=self.room, issuer=self.owner
        )
        await async_save(Message, message="message", sender=self.owner, room=self.room)

        # Test owner deleting
        message = f"/d {self.room.name} owner"
        await self.communicators[self.owner.username].send(message)
        assert await self.communicators[self.owner.username].receive() == message

        # Test Admins deleted
        assert not await async_filter(Admin, room=self.room)

        # Test Bans deleted
        assert not await async_filter(Ban, room=self.room)

        # Test Messages deleted
        assert not await async_filter(Message, room=self.room)

        # Test Room deleted
        assert not await async_try_get(Room, name=self.room.name)
