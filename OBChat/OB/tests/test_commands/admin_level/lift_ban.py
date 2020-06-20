"""
Tests the /lift command function (see OB.commands.admin_level.lift_ban()).

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
        pass

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
