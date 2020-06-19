"""
Tests the /ban command function (see OB.commands.admin_level.ban()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

import sqlite3

import asyncio

import django

from pytest import mark

from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import Ban, OBUser, Room
from OB.utilities.test import communicator_setup, communicator_teardown, database_setup, \
    database_teardown
from OB.utilities.database import async_add_occupants, async_delete, async_get, \
    async_model_list, async_save

@mark.asyncio
@mark.django_db()
async def test_ban():
    """
    Description:
        Tests the /ban command (see OB.commands.ban()).
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
        unlimited_admin_0 = await async_get(OBUser, username="unlimited_admin_0")
        limited_admin_0 = await async_get(OBUser, username="limited_admin_0")
        auth_user = await async_get(OBUser, username="auth_user")
        anon_0 = await async_get(OBUser, username=f"{ANON_PREFIX}0")
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")
        occupants = await async_model_list(room_0.occupants)

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test unauthenticated user banning error
        message = "/ban"
        correct_response = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "banning people."
        )
        await communicators[f"{ANON_PREFIX}0"].send(message)
        assert await communicators[f"{ANON_PREFIX}0"].receive() == message
        assert await communicators[f"{ANON_PREFIX}0"].receive() == correct_response

        # Test authenticated user banning error
        message = "/b"
        correct_response = (
            "That's a little outside your pay-grade. Only admins may ban users. "
            "Try to /apply to be an admin."
        )
        await communicators["auth_user"].send(message)
        assert await communicators["auth_user"].receive() == message
        assert await communicators["auth_user"].receive() == correct_response

        # Test no arguments error
        message = "/b"
        correct_response = "Usage: /ban <user1> <user2> ..."
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test absent target error
        message = "/b auth_user_1"
        correct_response = "Nobody named auth_user_1 in this room. Are you seeing things?"
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test self target error
        message = "/b limited_admin_0"
        correct_response = (
            "You can't ban yourself. Just leave the room. Or put yourself on time-out."
        )
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin banning owner error
        message = "/b owner"
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin banning unlimited admin error
        message = "/b unlimited_admin_0"
        correct_response = (
            "unlimited_admin_0 is an unlimited admin, so you can't ban them. Feel free to /elevate"
            " your complaints to someone who has more authority."
        )
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin banning limited admin error
        message = "/b limited_admin_1"
        correct_response = (
            "limited_admin_1 is an admin just like you, so you can't ban them. Feel free to "
            "/elevate your complaints to someone who has more authority."
        )
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin banning authenticated user
        message = "/b auth_user"
        await communicators["limited_admin_0"].send(message)
        sender_response = (
            "Banned:\n"
            "   auth_user\n"
            "That'll show them."
        )
        others_response = (
            "One or more users have been banned:\n"
            "   auth_user\n"
            "Let this be a lesson to you all."
        )
        assert await communicators["limited_admin_0"].receive() == message
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
        assert auth_user not in await async_model_list(room_0.occupants)
        ban = await async_get(Ban, user=auth_user)
        try:
            # This should time-out because the user is banned, so they cannot connect
            await communicators["auth_user"].connect()
            assert False
        except asyncio.TimeoutError:
            pass

        # Unban banned user, add banned user back to room occupants and reset Communicators
        await async_delete(ban)
        await communicator_teardown(communicators)
        # Anonymous users are deleted when they disconnect, so make an identical replacement
        anon_0 = await async_save(
            OBUser,
            id=anon_0.id,
            username=anon_0.username,
            is_anon=True
        )
        occupants = [anon_0 if user.id == anon_0.id else user for user in occupants]
        await async_add_occupants(room_0, occupants)
        communicators = await communicator_setup(room_0)

        # Test unlimited admin banning owner error
        message = "/b owner"
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        await communicators["unlimited_admin_0"].send(message)
        assert await communicators["unlimited_admin_0"].receive() == message
        assert await communicators["unlimited_admin_0"].receive() == correct_response

        # Test unlimited admin banning unlimited admin error
        message = "/b unlimited_admin_1"
        correct_response = (
            "unlimited_admin_1 is an unlimited admin just like you, so you can't ban them. Feel "
            "free to /elevate your complaints to someone who has more authority."
        )
        await communicators["unlimited_admin_0"].send(message)
        assert await communicators["unlimited_admin_0"].receive() == message
        assert await communicators["unlimited_admin_0"].receive() == correct_response

        # Test unlimited admin banning limited admin
        message = "/b limited_admin_0"
        await communicators["unlimited_admin_0"].send(message)
        sender_response = (
            "Banned:\n"
            "   limited_admin_0\n"
            "That'll show them."
        )
        others_response = (
            "One or more users have been banned:\n"
            "   limited_admin_0\n"
            "Let this be a lesson to you all."
        )
        assert await communicators["unlimited_admin_0"].receive() == message
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
        assert limited_admin_0 not in await async_model_list(room_0.occupants)
        ban = await async_get(Ban, user=limited_admin_0)
        try:
            # This should time-out because the user is banned, so they cannot connect
            await communicators["limited_admin_0"].connect()
            assert False
        except asyncio.TimeoutError:
            pass

        # Unban banned user, add banned user back to room occupants and reset Communicators
        await async_delete(ban)
        await communicator_teardown(communicators)
        # Anonymous users are deleted when they disconnect, so make an identical replacement
        anon_0 = await async_save(
            OBUser,
            id=anon_0.id,
            username=anon_0.username,
            is_anon=True
        )
        occupants = [anon_0 if user.id == anon_0.id else user for user in occupants]
        await async_add_occupants(room_0, occupants)
        communicators = await communicator_setup(room_0)

        # Test unlimited admin banning authenticated user
        message = "/b auth_user"
        await communicators["unlimited_admin_0"].send(message)
        sender_response = (
            "Banned:\n"
            "   auth_user\n"
            "That'll show them."
        )
        others_response = (
            "One or more users have been banned:\n"
            "   auth_user\n"
            "Let this be a lesson to you all."
        )
        assert await communicators["unlimited_admin_0"].receive() == message
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
        assert auth_user not in await async_model_list(room_0.occupants)
        ban = await async_get(Ban, user=auth_user)
        try:
            # This should time-out because the user is banned, so they cannot connect
            await communicators["auth_user"].connect()
            assert False
        except asyncio.TimeoutError:
            pass

        # Unban banned user, add banned user back to room occupants and reset Communicators
        await async_delete(ban)
        await communicator_teardown(communicators)
        # Anonymous users are deleted when they disconnect, so make an identical replacement
        anon_0 = await async_save(
            OBUser,
            id=anon_0.id,
            username=anon_0.username,
            is_anon=True
        )
        occupants = [anon_0 if user.id == anon_0.id else user for user in occupants]
        await async_add_occupants(room_0, occupants)
        communicators = await communicator_setup(room_0)

        # Test owner banning multiple users
        # TODO: Testing banning anonymous users is causing database lock
        message = f"/b unlimited_admin_0 limited_admin_0 auth_user" #, {ANON_PREFIX}0",
        await communicators["owner"].send(message)
        sender_response = (
            "Banned:\n"
            "   unlimited_admin_0\n"
            "   limited_admin_0\n"
            "   auth_user\n"
            # f"   {ANON_PREFIX}0"
            "That'll show them."
        )
        others_response = (
            "One or more users have been banned:\n"
            "   unlimited_admin_0\n"
            "   limited_admin_0\n"
            "   auth_user\n"
            # f"   {ANON_PREFIX}0\n"
            "Let this be a lesson to you all."
        )
        assert await communicators["owner"].receive() == message
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
        assert unlimited_admin_0 not in await async_model_list(room_0.occupants)
        assert limited_admin_0 not in await async_model_list(room_0.occupants)
        assert auth_user not in await async_model_list(room_0.occupants)
        # assert anon_0 not in await async_model_list(room_0.occupants)
        await async_get(Ban, user=unlimited_admin_0)
        await async_get(Ban, user=limited_admin_0)
        await async_get(Ban, user=auth_user)
        # await async_get(Ban, user=anon_0)
        try:
            # This should time-out because the user is banned, so they cannot connect
            await communicators["unlimited_admin_0"].connect()
            assert False
        except asyncio.TimeoutError:
            pass
        try:
            # This should time-out because the user is banned, so they cannot connect
            await communicators["limited_admin_0"].connect()
            assert False
        except asyncio.TimeoutError:
            pass
        try:
            # This should time-out because the user is banned, so they cannot connect
            await communicators["auth_user"].connect()
            assert False
        except asyncio.TimeoutError:
            pass
        # try:
        #     # This should time-out because the user is banned, so they cannot connect
        #     await communicators["anon_0"].connect()
        #     assert False
        # except asyncio.TimeoutError:
        #     pass


    # Occasionally test_ban() will crash because of a database lock from threading collisions
    # This is pytest clashing with Django Channels and does not happen during in live testing
    # Restart the test until it succeeds or fails from a relevant error
    except (django.db.utils.OperationalError, sqlite3.OperationalError):
        await communicator_teardown(communicators)
        await database_teardown()
        await test_ban()

    finally:
        await communicator_teardown(communicators)
        await database_teardown()
