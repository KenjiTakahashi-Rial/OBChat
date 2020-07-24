"""
WhoTest class container module.
"""

from pytest import mark

from OB.models import Room
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_save

class WhoTest(BaseCommandTest):
    """
    Class to test the /who command function (see OB.commands.user_level.who).
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
        Tests the /who command (see OB.commands.user_level.who).
        """

        # Test nonexistent room error
        message = "/who nonexistent_room"
        correct_response = (
            "nonexistent_room doesn't exist, so that probably means nobody is in there."
        )
        await self.test_isolated(self.owner, message, correct_response)

        # Create empty room
        empty_room = await async_save(
            Room,
            name="empty_room",
            display_name="EmptyRoom",
            owner=self.communicators["owner"].scope["user"]
        )

        # Test empty room error
        message = "/w empty_room"
        correct_response = f"{empty_room} is all empty!"
        await self.test_isolated(self.owner, message, correct_response)

        # Test current room with no argument
        message = "/w"
        correct_response = "\n".join([
            f"Users in {self.room}:",
            f"    {self.owner} [Owner] [you]",
            f"    {self.unlimited_admins[0]} [Admin]",
            f"    {self.unlimited_admins[1]} [Admin]",
            f"    {self.limited_admins[0]} [Admin]",
            f"    {self.limited_admins[1]} [Admin]",
            f"    {self.auth_users[0]}",
            f"    {self.auth_users[1]}",
            f"    {self.anon_users[0]}",
            f"    {self.anon_users[1]}\n"
        ])
        await self.test_isolated(self.owner, message, correct_response)

        # Test current room with explicit argument
        message = "/w room"
        await self.test_isolated(self.owner, message, correct_response)

        # Test duplicate room arguments
        message = "/w room room room"
        await self.test_isolated(self.owner, message, correct_response)

        # Test multiple arguments
        message = "/w room empty_room nonexistent_room"
        correct_response = "\n".join([
            f"{correct_response}",
            f"{empty_room} is all empty!",
            f"nonexistent_room doesn't exist, so that probably means nobody is in there."
        ])
        await self.test_isolated(self.owner, message, correct_response)
