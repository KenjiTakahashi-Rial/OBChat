"""
The BaseCommandTest superclass.
"""

import sqlite3

import django

from channels.db import database_sync_to_async

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import ANON_PREFIX, GroupTypes, SYSTEM_USERNAME
from OB.models import Admin, Ban, Message, OBUser, Room
from OB.utilities.database import async_model_list

class BaseCommandTest:
    def __init__(self):
        """
        Description:
            Declares the instance variables that be used for testing, includes communicators and
            database objects.
        """

        self.owner = OBUser()
        self.room = Room()
        self.unlimited_admins = []
        self.limited_admins = []
        self.auth_users = []
        self.anon_users = []
        self.communicators = {}

    @database_sync_to_async
    def database_setup(self, unlimited_admins=0, limited_admins=0, auth_users=0, anon_users=0):
        """
        Description:
            Sets up database objects required to test the commands.
        Arguments:
            **kwargs (int): The number of a type of user to create and add to the room.
        """

        OBUser(
            username=SYSTEM_USERNAME,
            email="ob-sys@ob.ob",
            password="ob-sys"
        ).save()

        self.owner = OBUser.objects.create_user(
            username="owner",
            email="owner@ob.ob",
            password="owner",
            display_name="Owner"
        ).save()

        self.room = Room(
            name="empty_room",
            display_name="EmptyRoom",
            owner=self.owner
        ).save()

        self.room.occupants.add(self.owner)

        for i in range(unlimited_admins):
            self.unlimited_admins += [
                OBUser.objects.create_user(
                    username=f"unlimited_admin_{i}",
                    email=f"unlimited_admin_{i}@ob.ob",
                    password=f"unlimited_admin_{i}",
                    display_name=f"UnlimitedAdmin{i}"
                )
            ]

            Admin(
                user=self.unlimited_admins[i],
                room=self.room,
                issuer=self.owner,
                is_limited=False
            )

            self.room.occupants.add(self.unlimited_admins[i])

        for i in range(limited_admins):
            self.limited_admins += [
                OBUser.objects.create_user(
                    username=f"limited_admin_{i}",
                    email=f"limited_admin_{i}@ob.ob",
                    password=f"limited_admin_{i}",
                    display_name=f"LimitedAdmin{i}"
                )
            ]

            Admin(
                user=self.limited_admins[i],
                room=self.room,
                issuer=self.owner,
                is_limited=True
            )

            self.room.occupants.add(self.limited_admins[i])

        for i in range(auth_users):
            self.auth_users += [
                OBUser.objects.create_user(
                    username=f"auth_user_{i}",
                    email=f"auth_user_{i}@ob.ob",
                    password=f"auth_user_{i}",
                    display_name=f"AuthUser{i}"
                )
            ]

            self.room.occupants.add(self.auth_users[i])

        for i in range(anon_users):
            self.anon_users += [
                OBUser.objects.create_user(
                    username=f"{ANON_PREFIX}{i}",
                    is_anon=True
                )
            ]

            self.room.occupants.add(self.anon_users[i])

    @database_sync_to_async
    def database_teardown(self):
        """
        Description:
            Cleans up the database objects used to test the commands.
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

        self.__init__()

    async def communicator_setup(self):
        """
        Description:
            Sets up the communicator objects used to test the commands.
        """

        for user in await async_model_list(self.room.occupants):
            self.communicators[user.username] = await OBCommunicator(
                user,
                GroupTypes.Room,
                self.room.name
            ).connect()

    async def communicator_teardown(self, safe=True):
        """
        Description:
            Cleans up the communicator objects used to test the commands.

        Arguments:
            safe (bool): Indicates whether to use "safe" disconnection, where the database is not
                accessed. Occupants and anonymous users are not deleted.
        """

        for communicator in self.communicators.values():
            try:
                await communicator.disconnect(code=("safe" if safe else 1000))
            except AttributeError:
                # The commnicator has already been disconnected
                # OB.consumers.disconnect() raises an AttributeError because OBConsumer.room is None
                pass
            except (django.db.utils.OperationalError, sqlite3.OperationalError):
                # The database is locked, but he current communicator disconnected before the error
                pass

        self.communicators.clear()

    async def tests(self):
        """
        Description:
            This is where the main implementation of the tests goes.
            This should not be called without first setting up the database and communicators.
        """

    @mark.asyncio
    @mark.django_db()
    async def run(self):
        """
        Description:
            Runs the command test, including all setup and teardown.
        """

        try:
            await self.database_setup()
            await self.communicator_setup()
            await self.tests()
        except (django.db.utils.OperationalError, sqlite3.OperationalError):
            # Occasionally, some tests will crash because of database lock from asynchronous
            # database access. This is simply pytest clashing with Django Channels and does
            # not happen during live testing. Therefore, restart the test until it succeeds
            # or until it fails from a relevant error.
            await self.communicator_teardown()
            await self.database_teardown()
            await self.run()
        finally:
            # Prevent following tests from failing their database setup if this test fails before
            # cleaning up the database. Normally, the built-in pytest teardown_function() may be
            # used for this, but it is not used because it causes database lock with Django
            # Channels.
            await self.communicator_teardown()
            await self.database_teardown()
