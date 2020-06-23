"""
Class to test the /kick command function (see OB.commands.admin_level.kick()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.communicators import OBCommunicator
from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import OBUser, Room
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_add_occupants, async_get, async_model_list, async_save, \
    async_try_get

class KickTest(BaseCommandTest):
    def __init__(self):
        """
        Description:
            Declares the instance variables that be used for testing, includes communicators and
            database objects.
        """

        super().__init__(unlimited_admins=2, limited_admins=2, auth_users=2, anon_users=2)

    @mark.asyncio
    @mark.django_db()
    async def tests(self):
        """
        Description:
            Tests the /kick command (see OB.commands.user_level.kick()).
        """

        # Test unauthenticated user kicking error
        message = "/kick"
        correct_response = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "kicking people."
        )
        await self.communicators[f"{ANON_PREFIX}0"].send(message)
        assert await self.communicators[f"{ANON_PREFIX}0"].receive() == message
        assert await self.communicators[f"{ANON_PREFIX}0"].receive() == correct_response

        # Test authenticated user kicking error
        message = "/k"
        correct_response = (
            "That's a little outside your pay-grade. Only admins may kick users. "
            "Try to /apply to be an admin."
        )
        await self.communicators["auth_user_0"].send(message)
        assert await self.communicators["auth_user_0"].receive() == message
        assert await self.communicators["auth_user_0"].receive() == correct_response

        # Test no arguments error
        message = "/k"
        correct_response = "Usage: /kick <user1> <user2> ..."
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test absent target error
        message = "/k auth_user_0_1"
        correct_response = "Nobody named auth_user_0_1 in this room. Are you seeing things?"
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test self target error
        message = "/k limited_admin_0"
        correct_response = (
            "You can't kick yourself. Just leave the room. Or put yourself on time-out."
        )
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking owner error
        message = "/k owner"
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking unlimited admin error
        message = "/k unlimited_admin_0"
        correct_response = (
            f"{self.unlimited_admins[0]} is an unlimited admin, so you can't kick them. Feel free to "
            "/elevate your complaints to someone who has more authority."
        )
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking limited admin error
        message = "/k limited_admin_1"
        correct_response = (
            f"{self.limited_admins[1]} is an admin just like you, so you can't kick them. Feel free to "
            "/elevate your complaints to someone who has more authority."
        )
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking authenticated user
        message = "/k auth_user_0"
        await self.communicators["limited_admin_0"].send(message)
        sender_response = "\n".join([
            "Kicked:",
            f"   {self.auth_users[0]}",
            "That'll show them."
        ])
        others_response = "\n".join([
            "One or more users have been kicked:",
            f"   {self.auth_users[0]}",
            "Let this be a lesson to you all."
        ])
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == sender_response
        assert (
            await self.communicators["owner"].receive() ==
            await self.communicators["unlimited_admin_0"].receive() ==
            await self.communicators["unlimited_admin_1"].receive() ==
            await self.communicators["limited_admin_0"].receive() ==
            await self.communicators["limited_admin_1"].receive() ==
            await self.communicators[f"{ANON_PREFIX}0"].receive() ==
            others_response
        )
        assert (await self.communicators["auth_user_0"].receive())["refresh"]
        assert (await self.communicators["auth_user_0"].receive_output())["type"] == "websocket.close"
        assert self.auth_users[0] not in await async_model_list(self.room.occupants)

        # Add kicked users back to room occupants and reset Communicators
        await self.communicator_teardown()
        # Anonymous users are deleted when they disconnect, so make an identical replacement
        for i in range(len(self.anon_users)):
            if await async_try_get(OBUser, id=self.anon_users[i].id):
                self.anon_users[i] = await async_save(
                    OBUser,
                    id=self.anon_users[i].id,
                    username=self.anon_users[i].username,
                    is_anon=True
                )
        await async_add_occupants(self.room, self.anon_users)
        await async_add_occupants(self.room, self.auth_users)
        await async_add_occupants(self.room, self.limited_admins)
        await async_add_occupants(self.room, self.unlimited_admins)
        await async_add_occupants(self.room, [self.owner])
        await self.communicator_setup()

        # Test unlimited admin kicking owner error
        message = "/k owner"
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        await self.communicators["unlimited_admin_0"].send(message)
        assert await self.communicators["unlimited_admin_0"].receive() == message
        assert await self.communicators["unlimited_admin_0"].receive() == correct_response

        # Test unlimited admin kicking unlimited admin error
        message = "/k unlimited_admin_1"
        correct_response = (
            f"{self.unlimited_admins[1]} is an unlimited admin just like you, so you can't kick them. "
            "Feel free to /elevate your complaints to someone who has more authority."
        )
        await self.communicators["unlimited_admin_0"].send(message)
        assert await self.communicators["unlimited_admin_0"].receive() == message
        assert await self.communicators["unlimited_admin_0"].receive() == correct_response

        # Test unlimited admin kicking limited admin
        message = "/k limited_admin_0"
        await self.communicators["unlimited_admin_0"].send(message)
        sender_response = "\n".join([
            "Kicked:",
            f"   {self.limited_admins[0]}",
            "That'll show them."
        ])
        others_response = "\n".join([
            "One or more users have been kicked:",
            f"   {self.limited_admins[0]}",
            "Let this be a lesson to you all."
        ])
        assert await self.communicators["unlimited_admin_0"].receive() == message
        assert await self.communicators["unlimited_admin_0"].receive() == sender_response
        assert (
            await self.communicators["owner"].receive() ==
            await self.communicators["unlimited_admin_0"].receive() ==
            await self.communicators["unlimited_admin_1"].receive() ==
            await self.communicators["limited_admin_1"].receive() ==
            await self.communicators["auth_user_0"].receive() ==
            await self.communicators[f"{ANON_PREFIX}0"].receive() ==
            others_response
        )
        assert (await self.communicators["limited_admin_0"].receive())["refresh"]
        assert (
            (await self.communicators["limited_admin_0"].receive_output())["type"] == "websocket.close"
        )
        assert self.limited_admins[0] not in await async_model_list(self.room.occupants)

        # Test unlimited admin kicking authenticated user
        message = "/k auth_user_0"
        await self.communicators["unlimited_admin_0"].send(message)
        sender_response = "\n".join([
            "Kicked:",
            f"   {self.auth_users[0]}",
            "That'll show them."
        ])
        others_response = "\n".join([
            "One or more users have been kicked:",
            f"   {self.auth_users[0]}",
            "Let this be a lesson to you all."
        ])
        assert await self.communicators["unlimited_admin_0"].receive() == message
        assert await self.communicators["unlimited_admin_0"].receive() == sender_response
        assert (
            await self.communicators["owner"].receive() ==
            await self.communicators["unlimited_admin_0"].receive() ==
            await self.communicators["unlimited_admin_1"].receive() ==
            await self.communicators["limited_admin_1"].receive() ==
            await self.communicators[f"{ANON_PREFIX}0"].receive() ==
            others_response
        )
        assert (await self.communicators["auth_user_0"].receive())["refresh"]
        assert (await self.communicators["auth_user_0"].receive_output())["type"] == "websocket.close"
        assert self.auth_users[0] not in await async_model_list(self.room.occupants)

        # Add kicked users back to room occupants and reset Communicators
        await self.communicator_teardown()
        # Anonymous users are deleted when they disconnect, so make an identical replacement
        for i in range(len(self.anon_users)):
            if await async_try_get(OBUser, id=self.anon_users[i].id):
                self.anon_users[i] = await async_save(
                    OBUser,
                    id=self.anon_users[i].id,
                    username=self.anon_users[i].username,
                    is_anon=True
                )
        await async_add_occupants(self.room, self.anon_users)
        await async_add_occupants(self.room, self.auth_users)
        await async_add_occupants(self.room, self.limited_admins)
        await async_add_occupants(self.room, self.unlimited_admins)
        await async_add_occupants(self.room, [self.owner])
        await self.communicator_setup()

        # Test owner kicking multiple users
        # TODO: Testing kicking anonymous users is causing database lock
        message = f"/k unlimited_admin_0 limited_admin_0 auth_user_0" #, {ANON_PREFIX}0",
        await self.communicators["owner"].send(message)
        sender_response = "\n".join([
            "Kicked:",
            f"   {self.unlimited_admins[0]}",
            f"   {self.limited_admins[0]}",
            f"   {self.auth_users[0]}",
            # f"   {self.anon_users[0]}",
            "That'll show them."
        ])
        others_response = "\n".join([
            "One or more users have been kicked:",
            f"   {self.unlimited_admins[0]}",
            f"   {self.limited_admins[0]}",
            f"   {self.auth_users[0]}",
            # f"   {self.anon_users[0]}",
            "Let this be a lesson to you all."
        ])
        assert await self.communicators["owner"].receive() == message
        assert await self.communicators["owner"].receive() == sender_response
        assert (
            await self.communicators["owner"].receive() ==
            await self.communicators["unlimited_admin_1"].receive() ==
            await self.communicators["limited_admin_1"].receive() ==
            others_response
        )
        assert (await self.communicators["unlimited_admin_0"].receive())["refresh"]
        assert (await self.communicators["limited_admin_0"].receive())["refresh"]
        assert (await self.communicators["auth_user_0"].receive())["refresh"]
        # assert (await self.communicators[f"{ANON_PREFIX}0"].receive())["refresh"]
        assert (
            (await self.communicators["unlimited_admin_0"].receive_output())["type"] == "websocket.close"
        )
        assert (
            (await self.communicators["limited_admin_0"].receive_output())["type"] == "websocket.close"
        )
        assert (await self.communicators["auth_user_0"].receive_output())["type"] == "websocket.close"
        # assert (
        #     (await self.communicators[f"{ANON_PREFIX}0"].receive_output())["type"] == "websocket.close"
        # )
        assert self.unlimited_admins[0] not in await async_model_list(self.room.occupants)
        assert self.limited_admins[0] not in await async_model_list(self.room.occupants)
        assert self.auth_users[0] not in await async_model_list(self.room.occupants)
        # assert anon_0 not in await async_model_list(room_0.occupants)
