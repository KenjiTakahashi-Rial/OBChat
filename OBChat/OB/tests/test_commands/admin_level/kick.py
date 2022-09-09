"""
KickTest class container module.
"""

from pytest import mark

from OB.models import OBUser
from OB.strings import StringId
from OB.tests.test_commands.base import BaseCommandTest
from OB.utilities.database import (
    async_add_occupants,
    async_model_list,
    async_save,
    async_try_get,
)


class KickTest(BaseCommandTest):
    """
    Class to test the /kick command function (see OB.commands.admin_level.kick).
    """

    def __init__(self):
        """
        Declares the instance variables that be used for testing, includes communicators and
        database objects.
        """

        super().__init__(unlimited_admins=2, limited_admins=2, auth_users=2, anon_users=2)

    @mark.asyncio
    @mark.django_db()
    async def tests(self):
        """
        Tests the /kick command (see OB.commands.user_level.kick).
        Tests errors last just in case previous tests fail and the test must run again.
        """

        # Test limited Admin kicking authenticated user
        await self.test_success(self.limited_admins[0], [self.auth_users[0]])

        # Test Unlimited Admin kicking limited admin
        await self.test_success(self.unlimited_admins[0], [self.limited_admins[0]])

        # Test Unlimited Admin kicking authenticated user
        await self.test_success(self.unlimited_admins[0], [self.auth_users[0]])

        # Test Unlimited Admin kicking multiple users
        await self.test_success(self.unlimited_admins[0], [self.limited_admins[0], self.auth_users[0]])

        # Test owner kicking multiple users
        # TODO: Testing kicking anonymous users is causing database lock
        await self.test_success(
            self.owner,
            [self.unlimited_admins[0], self.limited_admins[0], self.auth_users[0]],
        )

        # Test unauthenticated user kicking error
        message = "/kick"
        correct_response = StringId.AnonKicking
        await self.test_isolated(self.anon_users[0], message, correct_response)

        # Test authenticated user kicking error
        message = "/k"
        correct_response = StringId.NonAdminKicking
        await self.test_isolated(self.auth_users[0], message, correct_response)

        # Test no arguments error
        message = "/k"
        correct_response = StringId.KickSyntax
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test absent target error
        message = "/k auth_user_0_1"
        correct_response = StringId.UserNotPresent.format("auth_user_0_1")
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test self target error
        message = "/k limited_admin_0"
        correct_response = StringId.KickSelf
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test limited Admin kicking owner error
        message = "/k owner"
        correct_response = StringId.TargetOwner
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test limited Admin kicking Unlimited Admin error
        message = "/k unlimited_admin_0"
        correct_response = StringId.KickPeer.format(self.unlimited_admins[0], StringId.Unlimited + StringId.Admin)
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test limited Admin kicking limited Admin error
        message = "/k limited_admin_1"
        correct_response = StringId.KickPeer.format(self.limited_admins[1], StringId.Admin + StringId.JustLikeYou)
        await self.test_isolated(self.limited_admins[0], message, correct_response)

        # Test Unlimited Admin kicking owner error
        message = "/k owner"
        correct_response = StringId.TargetOwner
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

        # Test Unlimited Admin kicking Unlimited Admin error
        message = "/k unlimited_admin_1"
        correct_response = StringId.KickPeer.format(
            self.unlimited_admins[1],
            StringId.Unlimited + StringId.Admin + StringId.JustLikeYou,
        )
        await self.test_isolated(self.unlimited_admins[0], message, correct_response)

    @mark.asyncio
    @mark.django_db()
    async def test_success(self, sender, targets):
        """
        Tests a successful kick through the /kick command.

        Arguments:
            sender (OBUser): The user to send the /kick command.
            targets (list[OBUser]): The users to try to kick.
        """

        # Prepare the message and responses
        message = "/k"
        sender_response = StringId.KickSenderReceiptPreface + "\n"
        others_response = StringId.KickOccupantsNotificationPreface + "\n"

        for user in targets:
            message += f" {user.username}"
            sender_response += f"   {user}\n"
            others_response += f"   {user}\n"

        sender_response += StringId.KickSenderReceiptNote
        others_response += StringId.KickOccupantsNotificationNote

        # Send the command message
        await self.communicators[sender.username].send(message)

        # Test sender response
        assert await self.communicators[sender.username].receive() == message
        assert await self.communicators[sender.username].receive() == sender_response

        # Test others response
        occupants = await async_model_list(self.room.occupants)
        for user in occupants:
            if user not in targets and user != sender:
                assert await self.communicators[user.username].receive() == others_response

        # Test kicks
        for user in targets:
            assert (await self.communicators[user.username].receive())["refresh"]
            assert (await self.communicators[user.username].receive_output())["type"] == "websocket.close"
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
                    is_anon=True,
                )
        await async_add_occupants(self.room, self.anon_users)
        await async_add_occupants(self.room, self.auth_users)
        await async_add_occupants(self.room, self.limited_admins)
        await async_add_occupants(self.room, self.unlimited_admins)
        await async_add_occupants(self.room, [self.owner])
        await self.communicator_setup()
