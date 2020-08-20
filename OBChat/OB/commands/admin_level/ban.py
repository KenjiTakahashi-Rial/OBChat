"""
BanCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Ban, OBUser
from OB.strings import StringId
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_save, async_try_get
from OB.utilities.event import send_room_event

class BanCommand(BaseCommand):
    """
    Remove one or more OBConsumers from the group a Room is associated with and do not allow them
    to rejoin the group. Bans may be lifted (see lift()).
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticated user
        if self.sender_privilege < Privilege.AuthUser:
            self.sender_receipt = [StringId.AnonBanning]
        # Is authenticated, but not an admin
        elif self.sender_privilege < Privilege.Admin:
            self.sender_receipt = [StringId.NonAdminBanning]
        # Missing target arguments
        elif not self.args:
            self.sender_receipt = [StringId.BanSyntax]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_arguments().
        """

        for username in self.args:
            arg_user = await async_try_get(OBUser, username=username)

            if arg_user:
                arg_privilege = await async_get_privilege(arg_user, self.room)
                arg_ban = await async_try_get(Ban, user=arg_user, room=self.room, is_lifted=False)

            # Target user does not exist
            if not arg_user:
                self.sender_receipt += [StringId.UserNotPresent.format(username)]
            # Target user is the sender, themself
            elif arg_user == self.sender:
                self.sender_receipt += [StringId.BanSelf]
            # Target user is the owner
            elif arg_privilege == Privilege.Owner:
                self.sender_receipt += [StringId.BanOwner]
            # Target user is already banned
            elif arg_ban:
                self.sender_receipt += [StringId.AlreadyBanned]
            # Target user has Privilege greater than or equal to the sender
            elif arg_privilege >= self.sender_privilege:
                job_title = StringId.Admin

                if arg_privilege == await async_get_privilege(self.sender, self.room):
                    job_title += StringId.JustLikeYou

                if arg_privilege == Privilege.UnlimitedAdmin:
                    job_title = StringId.Unlimited + job_title

                self.sender_receipt += [StringId.BanPeer.format(arg_user, job_title)]
            # Target user is a valid ban
            else:
                self.valid_targets += [arg_user]

        return bool(self.valid_targets)

    async def execute_implementation(self):
        """
        Kick and ban users from the room.
        Constructs strings to send back to the sender and to the other occupants of the room.
        The sender receipt includes per-argument error messages.
        """

        ban_message_body = []

        for banned_user in self.valid_targets:
            # Save the ban to the database
            await async_save(
                Ban,
                user=banned_user,
                room=self.room,
                issuer=self.sender
            )

            # Kick the user
            kick_event = {
                "type": "kick",
                "target_id": banned_user.id
            }
            await send_room_event(self.room.id, kick_event)

            # Add the user's name to the sender receipt and occupants notification
            ban_message_body += [f"   {banned_user}"]

        self.sender_receipt += (
            # Add an exra newline to separate argument error messages from ban receipt
            [("\n" if self.sender_receipt else "") + StringId.BanSenderReceiptPreface] +
            ban_message_body +
            [StringId.BanSenderReceiptNote]
        )

        self.occupants_notification += (
            [StringId.BanOccupantsNotificationPreface] +
            ban_message_body +
            [StringId.BanOccupantsNotificationNote]
        )
