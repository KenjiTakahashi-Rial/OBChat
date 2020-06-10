"""
Tests the /room command function (see OB.commands.auth_user_level.create_room()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import OBUser, Room
from OB.utilities.test import communicator_setup, communicator_teardown, database_setup, \
    database_teardown
from OB.utilities.database import async_get

@mark.asyncio
@mark.django_db()
async def test_create_room():
    """
    Description:
        Tests the /room command (see OB.commands.user_level.create_room()).
        Wrapped in a try block to prevent following tests from failing their database setup if this
        test fails before cleaning up the database.
        Normally, the built-in pytest teardown_function() accounts for this, but it is not used
        for testing commands (see database_teardown()).
    """

    communicators = None

    try:
        # Database setup
        await database_setup()

        # Get database objects
        owner = await async_get(OBUser, username="owner")
        unlimited_admin_0 = await async_get(OBUser, username="unlimited_admin_0")
        anon_1 = await async_get(OBUser, username=f"{ANON_PREFIX}1")
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test no arguments error
        message = "/room"
        correct_response = "Usage: /room <name>"
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert await communicators["owner"].receive() == correct_response

        # Test unauthenticated user error
        message = "/r anon_room"
        correct_response = "Identify yourself! Must log in to create a room."
        await communicators[f"{ANON_PREFIX}0"].send(message)
        assert await communicators[f"{ANON_PREFIX}0"].receive() == message
        assert await communicators[f"{ANON_PREFIX}0"].receive() == correct_response

        # Test multiple arguments error
        message = "/r room 1"
        correct_response = "Room name cannot contain spaces."
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert await communicators["owner"].receive() == correct_response

        # Test existing room error
        message = "/r room_0"
        correct_response = "Someone beat you to it. room_0 already exists."
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert await communicators["owner"].receive() == correct_response

        # Test room creation
        message = "/r room_1"
        correct_response = "Sold! Check out your new room: room_1"
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert await communicators["owner"].receive() == correct_response
        room_1 = await async_get(Room, group_type=GroupTypes.Room, name="room_1")

        # Create WebsocketCommunicators to test new room
        communicators["owner_room_1"] = await OBCommunicator(
            owner,
            GroupTypes.Room,
            room_1.name
        ).connect()

        communicators["unlimited_admin_0_room_1"] = await OBCommunicator(
            unlimited_admin_0,
            GroupTypes.Room,
            room_1.name
        ).connect()

        communicators["anon_room_1"] = await OBCommunicator(
            anon_1,
            GroupTypes.Room,
            room_1.name
        ).connect()

        # Test new room messaging
        message = "So I heard you made a new room."
        await communicators["unlimited_admin_0_room_1"].send(message)
        assert (
            await communicators["owner_room_1"].receive() ==
            await communicators["unlimited_admin_0_room_1"].receive() ==
            await communicators["anon_room_1"].receive() ==
            message
        )

        message = "You heard right. How's the signal?"
        await communicators["owner_room_1"].send(message)
        assert (
            await communicators["owner_room_1"].receive() ==
            await communicators["unlimited_admin_0_room_1"].receive() ==
            await communicators["anon_room_1"].receive() ==
            message
        )

        message = "Can I join in on the fun?"
        await communicators["anon_room_1"].send(message)
        assert (
            await communicators["owner_room_1"].receive() ==
            await communicators["unlimited_admin_0_room_1"].receive() ==
            await communicators["anon_room_1"].receive() ==
            message
        )

    finally:
        await communicator_teardown(communicators)
        await database_teardown()
