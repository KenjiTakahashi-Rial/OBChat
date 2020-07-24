"""
Useful test functions.
"""

import sqlite3

import django

from channels.db import database_sync_to_async

from OB.communicators import OBCommunicator
from OB.constants import ANON_PREFIX, GroupTypes, SYSTEM_USERNAME
from OB.models import Admin, Ban, Message, OBUser, Room
from OB.utilities.database import add_occupants, async_model_list

# TODO: Go through these and remove unneeded ones.

@database_sync_to_async
def database_setup():
    """
    Sets up database objects required to test the commands.
    Ideally, the return value would be a dict of OBUsers and Rooms, but returning any database
    objects from this function will cause threading issues by locking the database.
    The built-in pytest setup fixture causes threading issues with the asynchronous command
    testing.
    """

    OBUser(
        username=SYSTEM_USERNAME,
        email="ob-sys@ob.ob",
        password="ob-sys"
    ).save()

    owner = OBUser(
        username="owner",
        email="owner@ob.ob",
        password="owner",
        display_name="Owner"
    ).save()

    unlimited_admin_0 = OBUser(
        username="unlimited_admin_0",
        email="unlimited_admin_0@ob.ob",
        password="unlimited_admin",
        display_name="UnlimitedAdmin0"
    ).save()

    unlimited_admin_1 = OBUser(
        username="unlimited_admin_1",
        email="unlimited_admin_1@ob.ob",
        password="unlimited_admin_1",
        display_name="UnlimitedAdmin1"
    ).save()

    limited_admin_0 = OBUser(
        username="limited_admin_0",
        email="limited_admin_0@ob.ob",
        password="limited_admin_0",
        display_name="LimitedAdmin0"
    ).save()

    limited_admin_1 = OBUser(
        username="limited_admin_1",
        email="limited_admin_1@ob.ob",
        password="limited_admin_1",
        display_name="LimitedAdmin1"
    ).save()

    auth_user_0 = OBUser(
        username="auth_user_0",
        email="auth_user_0@ob.ob",
        password="auth_user_0",
        display_name="AuthUser0"
    ).save()

    OBUser(
        username="auth_user_1",
        email="auth_user_1@ob.ob",
        password="auth_user_1",
        display_name="AuthUser1"
    ).save()

    anon_0 = OBUser(
        username=f"{ANON_PREFIX}0",
        is_anon=True
    ).save()

    OBUser(
        username=f"{ANON_PREFIX}1",
        is_anon=True
    ).save()

    room_0 = Room(
        name="room_0",
        display_name="Room0",
        owner=owner
    ).save()

    Room(
        name="empty_room",
        display_name="EmptyRoom",
        owner=unlimited_admin_0
    ).save()

    add_occupants(
        room_0,
        [
            owner,
            unlimited_admin_0,
            unlimited_admin_1,
            limited_admin_0,
            limited_admin_1,
            auth_user_0,
            anon_0
        ]
    )

    Admin(
        user=unlimited_admin_0,
        room=room_0,
        issuer=owner,
        is_limited=False
    ).save()

    Admin(
        user=unlimited_admin_1,
        room=room_0,
        issuer=owner,
        is_limited=False
    ).save()

    Admin(
        user=limited_admin_0,
        room=room_0,
        issuer=owner
    ).save()

    Admin(
        user=limited_admin_1,
        room=room_0,
        issuer=owner
    ).save()

@database_sync_to_async
def database_teardown():
    """
    Cleans up the database objects used to test the commands.
    The built-in pytest teardown fixture causes threading issues with the asynchronous command
    testing.
    """

    for admin in Admin.objects.all():
        admin.delete()

    for ban in Ban.objects.all():
        ban.delete()

    for message in Message.objects.all():
        message.delete()

    for ob_user in OBUser.objects.all():
        ob_user.delete()

    for room in Room.objects.all():
        room.delete()

async def communicator_setup(room):
    """
    Sets up the communicator objects used to test the commands.
    The built-in pytest setup fixture causes threading issues with the asynchronous command
    testing.

    Arguments:
        room (Room): The room to get a dict of communicators for.

    Return values:
        dict{string: OBCommunicator}: A dict with occupant usernames as keys and their
            Communicators as values.
    """

    communicators = {}

    for user in await async_model_list(room.occupants):
        communicators[user.username] = await OBCommunicator(
            user,
            GroupTypes.Room,
            room.name
        ).connect()

    return communicators

async def communicator_teardown(communicators, safe=True):
    """
    Cleans up the communicator objects used to test the commands.
    The built-in pytest teardown fixture causes threading issues with the asynchronous command
    testing.

    Arguments:
        communicators (dict{string: OBCommunicator}): The dict of communicators to clean up.
        safe (bool): Indicates whether to use "safe" disconnection, where the database is not
            accessed. Occupants and anonymous users are not deleted.
    """

    if not communicators:
        return

    for communicator in communicators.values():
        try:
            await communicator.disconnect(code=("safe" if safe else 1000))
        except AttributeError:
            # The commnicator has already been disconnected
            # OB.consumers.disconnect() raises an AttributeError because OBConsumer.room is None
            pass
        except (django.db.utils.OperationalError, sqlite3.OperationalError):
            # The database is locked, but he current communicator disconnected before the error
            pass

    communicators.clear()
