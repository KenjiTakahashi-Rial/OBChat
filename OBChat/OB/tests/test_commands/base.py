"""
The BaseCommandTest class container module.
"""

import sqlite3

import django

from channels.db import database_sync_to_async

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import GroupTypes
from OB.models import Admin, Ban, Message, OBUser, Room
from OB.strings import StringId
from OB.utilities.database import async_model_list


class BaseCommandTest:
    """
    A superclass for all command tests.
    Command tests follow require specific database and Communicator setup because of their effects
    on the database and use of WebSockets.
    """

    def __init__(self, unlimited_admins=0, limited_admins=0, auth_users=0, anon_users=0):
        """
        Declares the instance variables that be used for testing, includes communicators and
        database objects.

        Arguments:
            unlimited_admins (int): The number of Unlimited Admins that will be needed to test.
            limited_admins (int): The number of limited admins that will be needed to test.
            auth_users (int): The number of authenticated users that will be needed to test.
            anon_users (int): The number of anonymous users that will be needed to test.
        """

        self.owner = OBUser()
        self.room = Room()
        self.unlimited_admins = [None for i in range(unlimited_admins)]
        self.limited_admins = [None for i in range(limited_admins)]
        self.auth_users = [None for i in range(auth_users)]
        self.anon_users = [None for i in range(anon_users)]
        self.communicators = {}

    @database_sync_to_async
    def database_setup(self):
        """
        Sets up database objects required to test the commands.
        Creates users based on the number of users specified from __init__().
        """

        OBUser(username=StringId.SystemUsername, email="ob-sys@ob.ob", password="ob-sys").save()

        self.owner = OBUser.objects.create_user(
            username="owner",
            email="owner@ob.ob",
            password="owner",
            display_name="Owner",
        ).save()

        self.room = Room(name="room", display_name="Room", owner=self.owner).save()

        self.room.occupants.add(self.owner)

        for i in range(len(self.unlimited_admins)):
            self.unlimited_admins[i] = OBUser.objects.create_user(
                username=f"unlimited_admin_{i}",
                email=f"unlimited_admin_{i}@ob.ob",
                password=f"unlimited_admin_{i}",
                display_name=f"UnlimitedAdmin{i}",
            ).save()

            Admin(
                user=self.unlimited_admins[i],
                room=self.room,
                issuer=self.owner,
                is_limited=False,
            ).save()

            self.room.occupants.add(self.unlimited_admins[i])

        for i in range(len(self.limited_admins)):
            self.limited_admins[i] = OBUser.objects.create_user(
                username=f"limited_admin_{i}",
                email=f"limited_admin_{i}@ob.ob",
                password=f"limited_admin_{i}",
                display_name=f"LimitedAdmin{i}",
            ).save()

            Admin(
                user=self.limited_admins[i],
                room=self.room,
                issuer=self.owner,
                is_limited=True,
            ).save()

            self.room.occupants.add(self.limited_admins[i])

        for i in range(len(self.auth_users)):
            self.auth_users[i] = OBUser.objects.create_user(
                username=f"auth_user_{i}",
                email=f"auth_user_{i}@ob.ob",
                password=f"auth_user_{i}",
                display_name=f"AuthUser{i}",
            ).save()

            self.room.occupants.add(self.auth_users[i])

        for i in range(len(self.anon_users)):
            self.anon_users[i] = OBUser.objects.create_user(username=f"{StringId.AnonPrefix}{i}", is_anon=True).save()

            self.room.occupants.add(self.anon_users[i])

    @database_sync_to_async
    def database_teardown(self):
        """
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
        Sets up the communicator objects used to test the commands.
        """

        for user in await async_model_list(self.room.occupants):
            self.communicators[user.username] = await OBCommunicator(user, GroupTypes.Room, self.room.name).connect()

    async def communicator_teardown(self, safe=True):
        """
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
                # The database is locked, but the current communicator disconnected before the error
                pass

        self.communicators.clear()

    async def tests(self):
        """
        This is where the main implementation of the tests goes.
        This should not be called without first setting up the database and communicators.
        """

    @mark.asyncio
    @mark.django_db()
    async def run(self):
        """
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

    @mark.asyncio
    @mark.django_db()
    async def test_isolated(self, sender, message, response):
        """
        Tests that a command and response are only seen by the sender.

        Arguments:
            sender (OBUser): The user who sends the message and the only user who should receive a
                response.
            response (string): The response that the sender should receive.
        """

        await self.communicators[sender.username].send(message)

        all_users = self.anon_users + self.auth_users + self.limited_admins + self.unlimited_admins + [self.owner]

        for user in all_users:
            if user == sender:
                assert await self.communicators[user.username].receive() == message
                assert await self.communicators[user.username].receive() == response
            else:
                assert await self.communicators[user.username].receive_nothing()
