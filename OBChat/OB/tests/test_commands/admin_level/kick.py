"""
Tests the /kick command function (see OB.commands.admin_level.kick()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.commands.command_handler import handle_command
from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import OBUser, Room
from OB.utilities.test import communicator_setup, communicator_teardown, database_setup, \
    database_teardown
from OB.utilities.database import async_add_occupants, async_get, async_model_list, async_save

@mark.asyncio
@mark.django_db()
async def test_kick():
    """
    Description:
        Tests the /kick command (see OB.commands.kick()).
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
        limited_admin_0 = await async_get(OBUser, username="limited_admin_0")
        auth_user = await async_get(OBUser, username="auth_user")
        anon_0 = await async_get(OBUser, username=f"{ANON_PREFIX}0")
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")
        occupants = await async_model_list(room_0.occupants)

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test unauthenticated user kicking error
        await handle_command("/kick", anon_0, room_0)
        correct_response = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "kicking people."
        )
        assert await communicators[f"{ANON_PREFIX}0"].receive() == correct_response

        # Test authenticated user kicking error
        await handle_command("/k", auth_user, room_0)
        correct_response = (
            "That's a little outside your pay-grade. Only admins may kick users. "
            "Try to /apply to be an admin."
        )
        assert await communicators["auth_user"].receive() == correct_response

        # Test no arguments error
        await handle_command("/k", limited_admin_0, room_0)
        correct_response = "Usage: /kick <user1> <user2> ..."
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test absent target error
        await handle_command("/k auth_user_1", limited_admin_0, room_0)
        correct_response = "Nobody named auth_user_1 in this room. Are you seeing things?"
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test self target error
        await handle_command("/k limited_admin_0", limited_admin_0, room_0)
        correct_response = (
            "You can't kick yourself. Just leave the room. Or put yourself on time-out."
        )
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking owner error
        await handle_command("/k owner", limited_admin_0, room_0)
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking unlimited admin error
        await handle_command("/k unlimited_admin_0", limited_admin_0, room_0)
        correct_response = (
            "unlimited_admin_0 is an unlimited admin, so you can't kick them. Please direct all "
            "complaints to your local room owner, I'm sure they'll love some more paperwork to "
            "do..."
        )
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking limited admin error
        await handle_command("/k limited_admin_1", limited_admin_0, room_0)
        correct_response = (
            "limited_admin_1 is an admin just like you, so you can't kick them. Please direct all "
            "complaints to your local room owner, I'm sure they'll love some more paperwork to "
            "do..."
        )
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking authenticated user
        await handle_command("/k auth_user", limited_admin_0, room_0)
        sender_response = (
            "Kicked:\n"
            "   auth_user\n"
            "That'll show them."
        )
        others_response = (
            "One or more users have been kicked:\n"
            "   auth_user\n"
            "Let this be a lesson to you all."
        )
        assert auth_user not in await async_model_list(room_0.occupants)
        assert await communicators["limited_admin_0"].receive() == sender_response
        assert (
            await communicators["owner"].receive() ==
            await communicators["unlimited_admin_0"].receive() ==
            await communicators["unlimited_admin_1"].receive() ==
            await communicators["limited_admin_0"].receive() ==
            await communicators["limited_admin_1"].receive() ==
            await communicators[f"{ANON_PREFIX}0"].receive() ==
            others_response
        )
        assert (await communicators["auth_user"].receive())["refresh"]
        assert (await communicators["auth_user"].receive_output())["type"] == "websocket.close"

        # Add kicked users back to room occupants and reset Communicators
        await communicator_teardown(communicators)
        # Anonymous users are deleted when their OBConsumer disconnects, so make an identical one
        anon_0 = await async_save(
            OBUser,
            id=anon_0.id,
            username=anon_0.username,
            is_anon=True
        )
        occupants = [anon_0 if user.id == anon_0.id else user for user in occupants]
        await async_add_occupants(room_0, occupants)
        communicators = await communicator_setup(room_0)

        # Test unlimited admin kicking owner error
        await handle_command("/k owner", unlimited_admin_0, room_0)
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        assert await communicators["unlimited_admin_0"].receive() == correct_response

        # Test unlimited admin kicking unlimited admin error
        await handle_command("/k unlimited_admin_1", unlimited_admin_0, room_0)
        correct_response = (
            "unlimited_admin_1 is an unlimited admin just like you, so you can't kick them. Please"
            " direct all complaints to your local room owner, I'm sure they'll love some more "
            "paperwork to do..."
        )
        assert await communicators["unlimited_admin_0"].receive() == correct_response

        # Test unlimited admin kicking limited admin
        await handle_command("/k limited_admin_0", unlimited_admin_0, room_0)
        sender_response = (
            "Kicked:\n"
            "   limited_admin_0\n"
            "That'll show them."
        )
        others_response = (
            "One or more users have been kicked:\n"
            "   limited_admin_0\n"
            "Let this be a lesson to you all."
        )
        assert limited_admin_0 not in await async_model_list(room_0.occupants)
        assert await communicators["unlimited_admin_0"].receive() == sender_response
        assert (
            await communicators["owner"].receive() ==
            await communicators["unlimited_admin_0"].receive() ==
            await communicators["unlimited_admin_1"].receive() ==
            await communicators["limited_admin_1"].receive() ==
            await communicators["auth_user"].receive() ==
            await communicators[f"{ANON_PREFIX}0"].receive() ==
            others_response
        )
        assert (await communicators["limited_admin_0"].receive())["refresh"]
        assert (
            (await communicators["limited_admin_0"].receive_output())["type"] == "websocket.close"
        )

        # Test unlimited admin kicking authenticated user
        await handle_command("/k auth_user", unlimited_admin_0, room_0)
        sender_response = (
            "Kicked:\n"
            "   auth_user\n"
            "That'll show them."
        )
        others_response = (
            "One or more users have been kicked:\n"
            "   auth_user\n"
            "Let this be a lesson to you all."
        )
        assert auth_user not in await async_model_list(room_0.occupants)
        assert await communicators["unlimited_admin_0"].receive() == sender_response
        assert (
            await communicators["owner"].receive() ==
            await communicators["unlimited_admin_0"].receive() ==
            await communicators["unlimited_admin_1"].receive() ==
            await communicators["limited_admin_1"].receive() ==
            await communicators[f"{ANON_PREFIX}0"].receive() ==
            others_response
        )
        assert (await communicators["auth_user"].receive())["refresh"]
        assert (await communicators["auth_user"].receive_output())["type"] == "websocket.close"

        # Add kicked users back to room occupants and reset Communicators
        await communicator_teardown(communicators)
        # Anonymous users are deleted when their OBConsumer disconnects, so make an identical one
        anon_0 = await async_save(
            OBUser,
            id=anon_0.id,
            username=anon_0.username,
            is_anon=True
        )
        occupants = [anon_0 if user.id == anon_0.id else user for user in occupants]
        await async_add_occupants(room_0, occupants)
        communicators = await communicator_setup(room_0)

        # Test owner kicking multiple users
        await handle_command(
            # TODO: Testing kicking anonymous users is causing database lock
            f"/k unlimited_admin_0 limited_admin_0 auth_user", #{ANON_PREFIX}0",
            owner,
            room_0
        )
        sender_response = (
            "Kicked:\n"
            "   unlimited_admin_0\n"
            "   limited_admin_0\n"
            "   auth_user\n"
            # f"   {ANON_PREFIX}0"
            "That'll show them."
        )
        others_response = (
            "One or more users have been kicked:\n"
            "   unlimited_admin_0\n"
            "   limited_admin_0\n"
            "   auth_user\n"
            # f"   {ANON_PREFIX}0\n"
            "Let this be a lesson to you all."
        )
        assert unlimited_admin_0 not in await async_model_list(room_0.occupants)
        assert limited_admin_0 not in await async_model_list(room_0.occupants)
        assert auth_user not in await async_model_list(room_0.occupants)
        # assert anon_0 not in await async_model_list(room_0.occupants)
        assert await communicators["owner"].receive() == sender_response
        assert (
            await communicators["owner"].receive() ==
            await communicators["unlimited_admin_1"].receive() ==
            await communicators["limited_admin_1"].receive() ==
            others_response
        )
        assert (await communicators["unlimited_admin_0"].receive())["refresh"]
        assert (await communicators["limited_admin_0"].receive())["refresh"]
        assert (await communicators["auth_user"].receive())["refresh"]
        # assert (await communicators[f"{ANON_PREFIX}0"].receive())["refresh"]
        assert (
            (await communicators["unlimited_admin_0"].receive_output())["type"] == "websocket.close"
        )
        assert (
            (await communicators["limited_admin_0"].receive_output())["type"] == "websocket.close"
        )
        assert (await communicators["auth_user"].receive_output())["type"] == "websocket.close"
        # assert (
        #     (await communicators[f"{ANON_PREFIX}0"].receive_output())["type"] == "websocket.close"
        # )

    finally:
        await communicator_teardown(communicators)
        await database_teardown()