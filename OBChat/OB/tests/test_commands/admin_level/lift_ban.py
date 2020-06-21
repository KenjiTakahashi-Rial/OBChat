"""
Tests the /lift command function (see OB.commands.admin_level.lift_ban()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

import sqlite3

import asyncio

import django

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import Ban, OBUser, Room
from OB.utilities.test import communicator_setup, communicator_teardown, database_setup, \
    database_teardown
from OB.utilities.database import async_add_occupants, async_delete, async_get, \
    async_model_list, async_save

@mark.asyncio
@mark.django_db()
async def test_lift_ban():
    """
    Description:
        Tests the /lift command (see OB.commands.lift_ban()).
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
        auth_user_0 = await async_get(OBUser, username="auth_user_0")
        auth_user_1 = await async_get(OBUser, username="auth_user_1")
        anon_0 = await async_get(OBUser, username=f"{ANON_PREFIX}0")
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test unauthenticated user lifting error
        message = "/lift"
        correct_response = (
            "You are far from one who can lift bans. Log in and prove yourself an admin."
        )
        await communicators[f"{ANON_PREFIX}0"].send(message)
        assert await communicators[f"{ANON_PREFIX}0"].receive() == message
        assert await communicators[f"{ANON_PREFIX}0"].receive() == correct_response

        # Test authenticated user lifting error
        message = "/l"
        correct_response = (
            "A mere mortal like yourself does not have the power to lift bans. Try to /apply to be"
            " an admin and perhaps you may obtain this power if you are worthy."
        )
        await communicators["auth_user_0"].send(message)
        assert await communicators["auth_user_0"].receive() == message
        assert await communicators["auth_user_0"].receive() == correct_response

        # Test no arguments error
        message = "/l"
        correct_response = "Usage: /lift <user1> <user2> ..."
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test absent target error
        message = "/l auth_user_0_1"
        correct_response = (
            "No user named auth_user_0_1 has been banned from this room. How can one lift that "
            "which has not been banned?"
        )
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Create test ban
        await async_save(
            Ban,
            user=auth_user_1,
            room=room_0,
            issuer=owner
        )

        # Test limited admin lifting owner-issued ban error
        message = "/l auth_user_1"
        correct_response = (
            f"auth_user_1 was banned by {owner}. You cannot lift a ban issued by a user of equal "
            "or higher privilege than yourself. If you REALLY want to lift this ban you can "
            "/elevate to a higher authority."
        )
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test unlimited admin lifting owner-issued ban error
        message = "/l auth_user_1"
        await communicators["unlimited_admin_0"].send(message)
        assert await communicators["unlimited_admin_0"].receive() == message
        assert await communicators["unlimited_admin_0"].receive() == correct_response

        # Test owner lifting ban
        message = "/l auth_user_1"
        correct_response = "\n".join([
            "Ban lifted:",
            f"   {auth_user_1}",
            "Fully reformed and ready to integrate into society."
        ])
        await communicators["owner"].send(message)
        assert await communicators["owner"].receive() == message
        assert await communicators["owner"].receive() == correct_response
        communicators["auth_user_1"] = await OBCommunicator(
            auth_user_1,
            GroupTypes.Room,
            room_0.name
        ).connect()
        await communicators["auth_user_1"].disconnect()

        # Create test ban
        await async_save(
            Ban,
            user=auth_user_1,
            room=room_0,
            issuer=unlimited_admin_0
        )

        # Test limited admin lifting unlimited-admin-issued ban error
        message = "/l auth_user_1"
        correct_response = (
            f"auth_user_1 was banned by {unlimited_admin_0}. You cannot lift a ban issued by a "
            "user of equal or higher privilege than yourself. If you REALLY want to lift this ban "
            "you can /elevate to a higher authority."
        )
        await communicators["limited_admin_0"].send(message)
        assert await communicators["limited_admin_0"].receive() == message
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test unlimited admin lifting unlimited-admin-issued ban error
        message = "/l auth_user_1"
        await communicators["unlimited_admin_1"].send(message)
        assert await communicators["unlimited_admin_1"].receive() == message
        assert await communicators["unlimited_admin_1"].receive() == correct_response

        # Test unlimited admin lifting ban
        message = "/l auth_user_1"
        correct_response = "\n".join([
            "Ban lifted:",
            f"   {auth_user_1}",
            "Fully reformed and ready to integrate into society."
        ])
        await communicators["unlimited_admin_0"].send(message)
        assert await communicators["unlimited_admin_0"].receive() == message
        assert await communicators["unlimited_admin_0"].receive() == correct_response

    # Occasionally test_ban() will crash because of a database lock from threading collisions
    # This is pytest clashing with Django Channels and does not happen during in live testing
    # Restart the test until it succeeds or fails from a relevant error
    except (django.db.utils.OperationalError, sqlite3.OperationalError):
        await communicator_teardown(communicators)
        await database_teardown()
        await test_lift_ban()

    finally:
        await communicator_teardown(communicators)
        await database_teardown()