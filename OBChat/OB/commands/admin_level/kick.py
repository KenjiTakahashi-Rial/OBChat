"""
KickCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import OBUser
from OB.strings import StringId
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_model_list, async_try_get
from OB.utilities.event import send_room_event


class KickCommand(BaseCommand):
    """
    Remove one or more OBConsumers from the group a Room is associated with.
    Kicked users will not receive messages from the group until they rejoin the Room.
    """

    CALLERS = [StringId.KickCaller, StringId.KickCallerShort]
    MANUAL = StringId.KickManual

    # TODO: Add an option to do this silently (without notifying everyone)

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticted user
        if self.sender_privilege < Privilege.AuthUser:
            self.sender_receipt = [StringId.AnonKicking]
        # Is authenticated, but not an admin
        elif self.sender_privilege < Privilege.Admin:
            self.sender_receipt = [StringId.NonAdminKicking]
        # Missing target arguments
        elif not self.args:
            self.sender_receipt = [StringId.KickSyntax]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_arguments().
        """

        for username in self.args:
            arg_user = await async_try_get(OBUser, username=username)
            arg_privilege = Privilege.Invalid

            if arg_user:
                arg_privilege = await async_get_privilege(arg_user, self.room)

            # Target user is not present in the room
            if not arg_user or arg_user not in await async_model_list(self.room.occupants):
                self.sender_receipt += [StringId.UserNotPresent.format(username)]
            # Target user is the sender
            elif arg_user == self.sender:
                self.sender_receipt += [StringId.KickSelf]
            # Target user is the owner
            elif arg_privilege == Privilege.Owner:
                self.sender_receipt += [StringId.TargetOwner]
            # Target user has Privilege greater than or equal to the sender
            elif arg_privilege >= self.sender_privilege:
                job_title = StringId.Admin

                if arg_privilege == self.sender_privilege:
                    job_title += StringId.JustLikeYou

                if arg_privilege == Privilege.UnlimitedAdmin:
                    job_title = StringId.Unlimited + job_title

                self.sender_receipt += [StringId.KickPeer.format(arg_user, job_title)]
            # Is valid kick
            else:
                self.valid_targets += [arg_user]

        return bool(self.valid_targets)

    async def execute_implementation(self):
        """
        Kick users from the room.
        Construct strings to send back to the sender and to the other occupants of the room.
        The sender receipt includes per-argument error messages.
        """

        kick_message_body = []

        for kicked_user in self.valid_targets:
            # Kick the user
            kick_event = {"type": "kick", "target_id": kicked_user.id}
            await send_room_event(self.room.id, kick_event)

            # Notify others that a user was kicked
            kick_message_body += [f"   {kicked_user}"]

        self.sender_receipt += (
            # Add an exra newline to separate argument error messages from ban receipt
            [("\n" if self.sender_receipt else "") + StringId.KickSenderReceiptPreface]
            + kick_message_body
            + [StringId.KickSenderReceiptNote]
        )
        self.occupants_notification += (
            [StringId.KickOccupantsNotificationPreface] + kick_message_body + [StringId.KickOccupantsNotificationNote]
        )
