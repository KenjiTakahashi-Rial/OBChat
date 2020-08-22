"""
CreateTest class container module.
"""

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import GroupTypes
from OB.models import Room
from OB.strings import StringId
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_get

class CreateTest(BaseCommandTest):
    """
    Class to test the /create command function (see OB.commands.auth_user_level.create).
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
        Tests the /create command (see OB.commands.user_level.create).
        """

        # Test no arguments error
        message = "/create"
        correct_response = StringId.CreateSyntax
        await self.test_isolated(self.owner, message, correct_response)

        # Test unauthenticated user error
        message = "/c anon_room"
        correct_response = StringId.AnonCreating
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test multiple arguments error
        message = "/c room 1"
        correct_response = StringId.CreateSyntaxError
        await self.test_isolated(self.owner, message, correct_response)

        # Test existing room error
        message = "/c room"
        correct_response = StringId.CreateExistingRoom.format(self.room)
        await self.test_isolated(self.owner, message, correct_response)

        # Test room creation
        message = "/c room_1"
        correct_response = StringId.CreateSenderReceipt.format("room_1")
        await self.communicators["owner"].send(message)
        assert await self.communicators["owner"].receive() == message
        assert await self.communicators["owner"].receive() == correct_response
        room_1 = await async_get(Room, group_type=GroupTypes.Room, name="room_1")

        # Create WebsocketCommunicators to test new room
        self.communicators["owner_room_1"] = await OBCommunicator(
            self.owner,
            GroupTypes.Room,
            room_1.name
        ).connect()

        self.communicators["unlimited_admin_0_room_1"] = await OBCommunicator(
            self.unlimited_admins[0],
            GroupTypes.Room,
            room_1.name
        ).connect()

        self.communicators["anon_room_1"] = await OBCommunicator(
            self.anon_users[1],
            GroupTypes.Room,
            room_1.name
        ).connect()

        # Test new room messaging
        message = "So I heard you made a new room."
        await self.communicators["unlimited_admin_0_room_1"].send(message)
        assert (
            await self.communicators["owner_room_1"].receive() ==
            await self.communicators["unlimited_admin_0_room_1"].receive() ==
            await self.communicators["anon_room_1"].receive() ==
            message
        )

        message = "You heard right. How's the signal?"
        await self.communicators["owner_room_1"].send(message)
        assert (
            await self.communicators["owner_room_1"].receive() ==
            await self.communicators["unlimited_admin_0_room_1"].receive() ==
            await self.communicators["anon_room_1"].receive() ==
            message
        )

        message = "Can I join in on the fun?"
        await self.communicators["anon_room_1"].send(message)
        assert (
            await self.communicators["owner_room_1"].receive() ==
            await self.communicators["unlimited_admin_0_room_1"].receive() ==
            await self.communicators["anon_room_1"].receive() ==
            message
        )
