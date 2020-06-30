"""
Class to test the /kick command function (see OB.commands.admin_level.kick()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.constants import ANON_PREFIX
from OB.models import OBUser
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import async_add_occupants, async_model_list, async_save, \
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
            f"{self.unlimited_admins[0]} is an unlimited admin, so you can't kick them. Feel free "
            "to /elevate your complaints to someone who has more authority."
        )
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking limited admin error
        message = "/k limited_admin_1"
        correct_response = (
            f"{self.limited_admins[1]} is an admin just like you, so you can't kick them. Feel "
            "free to /elevate your complaints to someone who has more authority."
        )
        await self.communicators["limited_admin_0"].send(message)
        assert await self.communicators["limited_admin_0"].receive() == message
        assert await self.communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking authenticated user
        await self.test_success(self.limited_admins[0], [self.auth_users[0]])

        # Test unlimited admin kicking owner error
        message = "/k owner"
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        await self.communicators["unlimited_admin_0"].send(message)
        assert await self.communicators["unlimited_admin_0"].receive() == message
        assert await self.communicators["unlimited_admin_0"].receive() == correct_response

        # Test unlimited admin kicking unlimited admin error
        message = "/k unlimited_admin_1"
        correct_response = (
            f"{self.unlimited_admins[1]} is an unlimited admin just like you, so you can't kick "
            "them. Feel free to /elevate your complaints to someone who has more authority."
        )
        await self.communicators["unlimited_admin_0"].send(message)
        assert await self.communicators["unlimited_admin_0"].receive() == message
        assert await self.communicators["unlimited_admin_0"].receive() == correct_response

        # Test unlimited admin kicking limited admin
        await self.test_success(self.unlimited_admins[0], [self.limited_admins[0]])

        # Test unlimited admin kicking authenticated user
        await self.test_success(self.unlimited_admins[0], [self.auth_users[0]])

        # Test unlimited admin kicking multiple users
        await self.test_success(
            self.unlimited_admins[0],
            [self.limited_admins[0], self.auth_users[0]]
        )

        # Test owner kicking multiple users
        # TODO: Testing kicking anonymous users is causing database lock
        await self.test_success(
            self.owner,
            [self.unlimited_admins[0], self.limited_admins[0], self.auth_users[0]]
        )

    @mark.asyncio
    @mark.django_db()
    async def test_success(self, sender, targets):
        """
        Description:
            Tests a successful kick through the /kick command.
        Arguments:
            sender (OBUser): The user to send the /kick command.
            targets (list[OBUser]): The users to try to kick.
        """

        # Prepare the message and responses
        message = "/k"
        sender_response = "Kicked:\n"
        others_response = "One or more users have been kicked:\n"

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

        # Test kicks
        for user in targets:
            assert (await self.communicators[user.username].receive())["refresh"]
            assert (
                (await self.communicators[user.username].receive_output())["type"]
                == "websocket.close"
            )
            assert user not in occupants

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
