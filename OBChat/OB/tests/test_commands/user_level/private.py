"""
Class to test the /private command function (see OB.commands.user_level.private).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import GroupTypes
from OB.models import Room
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_get
from OB.utilities.format import get_group_name

class PrivateTest(BaseCommandTest):
    def __init__(self):
        """
        Description:
            Declares the instance variables that be used for testing, includes communicators and
            database objects.
        """

        super().__init__(unlimited_admins=1, limited_admins=1, auth_users=1, anon_users=1)

    @mark.asyncio
    @mark.django_db()
    async def tests(self):
        """
        Description:
            Tests the /private command (see OB.commands.user_level.private).
        """

        # Test no arguments error
        message = "/private"
        correct_response = "Usage: /private /<user> <message>"
        await self.test_isolated(self.owner, message, correct_response)

        # Test missing "/" error
        message = "/p no_slash"
        correct_response = "Looks like you forgot a \"/\" before the username. I'll let it slide."
        await self.test_isolated(self.owner, message, correct_response)

        # Test nonexistent recipient error
        message = "/p /nonexistent_user"
        correct_response = (
            "nonexistent_user doesn't exist. Your private message will broadcasted into space "
            "instead."
        )
        await self.test_isolated(self.owner, message, correct_response)

        # Test empty message error
        message = "/p /unlimited_admin_0"
        correct_response = "No message specified. Did you give up at just the username?"
        await self.test_isolated(self.owner, message, correct_response)

        # Test private room auto-creation
        message = "/p /owner What's it like to own room_0?"
        await self.communicators["unlimited_admin_0"].send(message)
        assert await self.communicators["unlimited_admin_0"].receive() == message
        await async_get(
            Room,
            group_type=GroupTypes.Private,
            name=get_group_name(GroupTypes.Private, self.owner.id, self.unlimited_admins[0].id)
        )

        # Create WebsocketCommunicators to test private messaging
        self.communicators["owner_private"] = await OBCommunicator(
            self.owner,
            GroupTypes.Private,
            self.unlimited_admins[0].username
        ).connect()
        self.communicators["unlimited_admin_0_private"] = await OBCommunicator(
            self.unlimited_admins[0],
            GroupTypes.Private,
            self.owner.username
        ).connect()

        # Test private messaging
        message = "/p /unlimited_admin_0 It's pretty cool."
        correct_response = "It's pretty cool."
        await self.communicators["owner"].send(message)
        assert await self.communicators["owner"].receive() == message
        assert (
            await self.communicators["owner_private"].receive() ==
            await self.communicators["unlimited_admin_0_private"].receive() ==
            correct_response
        )
