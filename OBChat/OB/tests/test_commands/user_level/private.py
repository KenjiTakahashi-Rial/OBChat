"""
Tests the /private command function (see OB.commands.user_level.private()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import GroupTypes
from OB.models import OBUser, Room
from OB.utilities.test import communicator_setup, communicator_teardown, database_setup, \
    database_teardown
from OB.utilities.database import async_get
from OB.utilities.format import get_group_name

@mark.asyncio
@mark.django_db()
async def test_private():
    """
    Description:
        Tests the /private command (see OB.commands.user_level.private()).
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
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test no arguments error
        message = "/private"
        correct_response = "Usage: /private /<user> <message>"
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert await communicators["owner"].receive() == correct_response

        # Test missing "/" error
        message = "/p no_slash"
        correct_response = "Looks like you forgot a \"/\" before the username. I'll let it slide."
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert await communicators["owner"].receive() == correct_response

        # Test nonexistent recipient error
        message = "/p /nonexistent_user"
        correct_response = (
            "nonexistent_user doesn't exist. Your private message will broadcasted into space "
            "instead."
        )
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert await communicators["owner"].receive() == correct_response

        # Test empty message error
        message = "/p /unlimited_admin_0"
        correct_response = "No message specified. Did you give up at just the username?"
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert await communicators["owner"].receive() == correct_response

        # Test private room auto-creation
        message = "/p /owner What's it like to own room_0?"
        await communicators["unlimited_admin_0"].send(message)
        assert await communicators["unlimited_admin_0"].receive() == message
        await async_get(
            Room,
            group_type=GroupTypes.Private,
            name=get_group_name(GroupTypes.Private, owner.id, unlimited_admin_0.id)
        )

        # Create WebsocketCommunicators to test private messaging
        communicators["owner_private"] = await OBCommunicator(
            owner,
            GroupTypes.Private,
            unlimited_admin_0.username
        ).connect()
        communicators["unlimited_admin_0_private"] = await OBCommunicator(
            unlimited_admin_0,
            GroupTypes.Private,
            owner.username
        ).connect()

        # Test private messaging
        message = "/p /unlimited_admin_0 It's pretty cool."
        correct_response = "It's pretty cool."
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert (
            await communicators["owner_private"].receive() ==
            await communicators["unlimited_admin_0_private"].receive() ==
            correct_response
        )

    finally:
        await communicator_teardown(communicators)
        await database_teardown()
