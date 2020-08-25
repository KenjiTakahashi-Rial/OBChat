"""
PrivateTest class container module.
"""

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import GroupTypes
from OB.models import Room
from OB.strings import StringId
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_get
from OB.utilities.format import get_group_name

class PrivateTest(BaseCommandTest):
    """
    Class to test the /private command function (see OB.commands.user_level.private).
    """

    def __init__(self):
        """
        Declares the instance variables that be used for testing, includes communicators and
        database objects.
        """

        super().__init__(unlimited_admins=1, limited_admins=1, auth_users=1, anon_users=1)

    @mark.asyncio
    @mark.django_db()
    async def tests(self):
        """
        Tests the /private command (see OB.commands.user_level.private).
        """

        # Test no arguments error
        message = "/private"
        correct_response = StringId.PrivateSyntax
        await self.test_isolated(self.owner, message, correct_response)

        # Test missing "/" error
        message = "/p no_slash"
        correct_response = StringId.PrivateInvalidSyntax
        await self.test_isolated(self.owner, message, correct_response)

        # Test nonexistent recipient error
        message = "/p /nonexistent_user"
        correct_response = StringId.PrivateInvalidTarget.format("nonexistent_user")
        await self.test_isolated(self.owner, message, correct_response)

        # Test empty message error
        message = "/p /unlimited_admin_0"
        correct_response = StringId.PrivateNoMessage
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

    # TODO: Make a test_success method