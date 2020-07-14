"""
Class to test the /ban command function (see OB.commands.admin_level.ban).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

import asyncio

from pytest import mark

from OB.models import Ban, OBUser
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_add_occupants, async_delete, async_get, async_model_list, \
    async_save, async_try_get

class BanTest(BaseCommandTest):
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
            Tests the /ban command (see OB.commands.user_level.ban).
            Tests errors last just in case previous tests fail and the test must run again.
        """

        # Test limited Admin banning authenticated user
        message = "/b auth_user_0"
        await self.test_success(
            self.limited_admins[0],
            [self.auth_users[0]]
        )

        # Test Unlimited Admin banning limited admin
        await self.test_success(
            self.unlimited_admins[0],
            [self.limited_admins[0]]
        )

        # Test Unlimited Admin banning authenticated user
        await self.test_success(
            self.unlimited_admins[0],
            [self.auth_users[0]]
        )

        # Test owner banning multiple users
        # TODO: Testing banning anonymous users is causing database lock
        await self.test_success(
            self.owner,
            [self.unlimited_admins[0], self.limited_admins[0], self.auth_users[0]]
        )

        # Test unauthenticated user banning error
        message = "/ban"
        correct_response = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "banning people."
        )
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test authenticated user banning error
        message = "/b"
        correct_response = (
            "That's a little outside your pay-grade. Only admins may ban users. "
            "Try to /apply to be an Admin."
        )
        await self.test_isolated(self.auth_users[0], message, correct_response)

        # Test no arguments error
        message = "/b"
        correct_response = "Usage: /ban <user1> <user2> ..."
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test absent target error
        message = "/b auth_user_0_1"
        correct_response = "Nobody named auth_user_0_1 in this room. Are you seeing things?"
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test self target error
        message = "/b limited_admin_0"
        correct_response = (
            "You can't ban yourself. Just leave the room. Or put yourself on time-out."
        )
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test limited Admin banning owner error
        message = "/b owner"
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test limited Admin banning Unlimited Admin error
        message = "/b unlimited_admin_0"
        correct_response = (
            f"{self.unlimited_admins[0]} is an Unlimited Admin, so you can't ban them. Feel free "
            "to /elevate your complaints to someone who has more authority."
        )
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test limited Admin banning limited Admin error
        message = "/b limited_admin_1"
        correct_response = (
            f"{self.limited_admins[1]} is an Admin just like you, so you can't ban them. Feel "
            "free to /elevate your complaints to someone who has more authority."
        )
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test Unlimited Admin banning owner error
        message = "/b owner"
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin banning Unlimited Admin error
        message = "/b unlimited_admin_1"
        correct_response = (
            f"{self.unlimited_admins[1]} is an Unlimited Admin just like you, so you can't ban "
            "them. Feel free to /elevate your complaints to someone who has more authority."
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

    @mark.asyncio
    @mark.django_db()
    async def test_success(self, sender, targets):
        """
        Description:
            Tests a successful ban through the /ban command.
        Arguments:
            sender (OBUser): The user to send the /ban command.
            targets (list[OBUser]): The users to try to ban.
        """

        # Prepare the message and responses
        message = "/b"
        sender_response = "Banned:\n"
        others_response = "One or more users have been banned:\n"

        for user in targets:
            message += f" {user.username}"
            sender_response += f"   {user}\n"
            others_response += f"   {user}\n"

        sender_response += "That'll show them."
        others_response += "Let this be a lesson to you all."


        # Send the command message
        await self.communicators[sender.username].send(message)

        # Test sender response
        assert await self.communicators[sender.username].receive() == message
        assert await self.communicators[sender.username].receive() == sender_response

        # Test others response
        occupants = await async_model_list(self.room.occupants)

        for user in occupants:
            if user not in targets:
                assert await self.communicators[user.username].receive() == others_response

        for user in targets:
            # Test auto-kick
            assert (await self.communicators[user.username].receive())["refresh"]
            assert (
                (await self.communicators[user.username].receive_output())["type"]
                == "websocket.close"
            )
            assert user not in occupants

            # Test ban
            ban = await async_get(Ban, user=user)
            try:
                # This should time-out because the user is banned, so they cannot connect
                await self.communicators[user.username].connect()
                assert False
            except asyncio.TimeoutError:
                pass

            # Remove ban
            await async_delete(ban)

        # Add banned users back to room occupants and reset Communicators
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
