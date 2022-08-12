"""
BanTest class container module.
"""

import asyncio

from pytest import mark

from OB.models import Ban, OBUser
from OB.strings import StringId
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import (
    async_add_occupants,
    async_delete,
    async_get,
    async_model_list,
    async_save,
    async_try_get,
)


class BanTest(BaseCommandTest):
    """
    Class to test the /ban command function (see OB.commands.admin_level.ban).
    """

    def __init__(self):
        """
        Declares the instance variables that be used for testing, includes communicators and
        database objects.
        """

        super().__init__(
            unlimited_admins=2, limited_admins=2, auth_users=2, anon_users=2
        )

    @mark.asyncio
    @mark.django_db()
    async def tests(self):
        """
        Tests the /ban command (see OB.commands.user_level.ban).
        Tests errors last just in case previous tests fail and the test must run again.
        """

        # Test limited Admin banning authenticated user
        message = "/b auth_user_0"
        await self.test_success(self.limited_admins[0], [self.auth_users[0]])

        # Test Unlimited Admin banning limited admin
        await self.test_success(self.unlimited_admins[0], [self.limited_admins[0]])

        # Test Unlimited Admin banning authenticated user
        await self.test_success(self.unlimited_admins[0], [self.auth_users[0]])

        # Test owner banning multiple users
        await self.test_success(
            self.owner,
            [self.unlimited_admins[0], self.limited_admins[0], self.auth_users[0]],
        )

        # Test unauthenticated user banning error
        message = "/ban"
        correct_response = StringId.AnonBanning
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test authenticated user banning error
        message = "/b"
        correct_response = StringId.NonAdminBanning
        await self.test_isolated(self.auth_users[0], message, correct_response)

        # Test no arguments error
        message = "/b"
        correct_response = StringId.BanSyntax
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test absent target error
        message = "/b absent_user"
        correct_response = StringId.UserNotPresent.format("absent_user")
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test self target error
        message = "/b limited_admin_0"
        correct_response = StringId.BanSelf
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test limited Admin banning owner error
        message = "/b owner"
        correct_response = StringId.TargetOwner
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test limited Admin banning Unlimited Admin error
        message = "/b unlimited_admin_0"
        correct_response = StringId.BanPeer.format(
            f"{self.unlimited_admins[0]}", StringId.Unlimited + StringId.Admin
        )
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test limited Admin banning limited Admin error
        message = "/b limited_admin_1"
        correct_response = StringId.BanPeer.format(
            f"{self.limited_admins[1]}", StringId.Admin + StringId.JustLikeYou
        )
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test Unlimited Admin banning owner error
        message = "/b owner"
        correct_response = StringId.TargetOwner
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin banning Unlimited Admin error
        message = "/b unlimited_admin_1"
        correct_response = StringId.BanPeer.format(
            f"{self.unlimited_admins[1]}",
            StringId.Unlimited + StringId.Admin + StringId.JustLikeYou,
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Owner banning already banned user error
        await async_save(
            Ban, user=self.auth_users[0], room=self.room, issuer=self.owner
        )

        message = "/b auth_user_0"
        correct_response = StringId.AlreadyBanned
        await self.test_isolated(self.owner, message, correct_response)

    @mark.asyncio
    @mark.django_db()
    async def test_success(self, sender, targets, should_delete_ban=True):
        """
        Tests a successful ban through the /ban command.

        Arguments:
            sender (OBUser): The user to send the /ban command.
            targets (list[OBUser]): The users to try to ban.
        """

        # Prepare the message and responses
        message = "/b"
        sender_response = StringId.BanSenderReceiptPreface + "\n"
        others_response = StringId.BanOccupantsNotificationPreface + "\n"

        for user in targets:
            message += f" {user.username}"
            sender_response += f"   {user}\n"
            others_response += f"   {user}\n"

        sender_response += StringId.BanSenderReceiptNote
        others_response += StringId.BanOccupantsNotificationNote

        # Send the command message
        await self.communicators[sender.username].send(message)

        # Test sender response
        assert await self.communicators[sender.username].receive() == message
        assert await self.communicators[sender.username].receive() == sender_response

        # Test others response
        occupants = await async_model_list(self.room.occupants)

        for user in occupants:
            if user not in targets and user != sender:
                assert (
                    await self.communicators[user.username].receive() == others_response
                )

        for user in targets:
            # Test auto-kick
            assert (await self.communicators[user.username].receive())["refresh"]
            assert (await self.communicators[user.username].receive_output())[
                "type"
            ] == "websocket.close"
            assert user not in occupants

            # Test ban
            ban = await async_get(Ban, user=user)
            try:
                # This should time-out because the user is banned, so they cannot connect
                await self.communicators[user.username].connect()
                assert False
            except asyncio.TimeoutError:
                pass

            if should_delete_ban:
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
                    is_anon=True,
                )
        await async_add_occupants(self.room, self.anon_users)
        await async_add_occupants(self.room, self.auth_users)
        await async_add_occupants(self.room, self.limited_admins)
        await async_add_occupants(self.room, self.unlimited_admins)
        await async_add_occupants(self.room, [self.owner])
        await self.communicator_setup()
