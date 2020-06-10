"""
Tests the /who command function (see OB.commands.user_level.who()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.commands.command_handler import handle_command
from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import OBUser, Room
from OB.utilities.test import communicator_setup, communicator_teardown, database_setup, \
    database_teardown
from OB.utilities.database import async_get

@mark.asyncio
@mark.django_db()
async def test_who():
    """
    Description:
        Tests the /who command (see OB.commands.user_level.who()).
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
        unlimited_admin_1 = await async_get(OBUser, username="unlimited_admin_1")
        limited_admin_0 = await async_get(OBUser, username="limited_admin_0")
        limited_admin_1 = await async_get(OBUser, username="limited_admin_1")
        auth_user = await async_get(OBUser, username="auth_user")
        anon_0 = await async_get(OBUser, username=f"{ANON_PREFIX}0")
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test nonexistent room error
        message = "/who nonexistent_room"
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        correct_response = (
            "nonexistent_room doesn't exist, so that probably means nobody is in therea."
        )
        assert await communicators["owner"].receive() == correct_response

        # Test empty room error
        await handle_command("/w empty_room", owner, room_0)
        correct_response = "empty_room is all empty!"
        assert await communicators["owner"].receive() == correct_response

        # Test current room with no argument
        await handle_command("/w", owner, room_0)
        correct_response = "\n".join([
            "Users in room_0:",
            f"    {owner} [owner] [you]",
            f"    {unlimited_admin_0} [admin]",
            f"    {unlimited_admin_1} [admin]",
            f"    {limited_admin_0} [admin]",
            f"    {limited_admin_1} [admin]",
            f"    {auth_user}",
            f"    {anon_0}\n"
        ])
        assert await communicators["owner"].receive() == correct_response

        # Test current room with explicit argument
        await handle_command("/w room_0", owner, room_0)
        assert await communicators["owner"].receive() == correct_response

        # Test duplicate room arguments
        await handle_command("/w room_0 room_0 room_0", owner, room_0)
        assert await communicators["owner"].receive() == correct_response

        # Test multiple arguments
        await handle_command("/w room_0 empty_room nonexistent_room", owner, room_0)
        correct_response = (
            f"{correct_response}\n"
            "empty_room is all empty!\n"
            "nonexistent_room doesn't exist, so that probably means nobody is in there."
        )
        assert await communicators["owner"].receive() == correct_response

    finally:
        await communicator_teardown(communicators)
        await database_teardown()
