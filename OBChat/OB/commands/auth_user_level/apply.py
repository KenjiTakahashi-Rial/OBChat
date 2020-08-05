"""
ApplyCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_filter, async_get
from OB.utilities.event import send_system_room_message

class ApplyCommand(BaseCommand):
    """
    Sends a request for a user to be hired as an Admin or promoted to Unlimited Admin.
    The request is visible by all users with hiring privileges of the room.
    Optionally includes a message.
    """

    def __init__(self):
        """
        Apply requires an instance variable for sending the message to specific users.
        """

        super().__init__()
        self.targets_message = []

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticated user
        if self.sender_privilege < Privilege.AuthUser:
            self.sender_receipt += [
                "You can't get hired looking like that! Clean yourself up and make an account "
                "first."
            ]
        # Is already an Unlimited Admin
        elif self.sender_privilege >= Privilege.UnlimitedAdmin:
            self.sender_receipt += [
                "You're already a big shot Unlimited Admin! There's nothing left to apply to."
            ]

        return not self.sender_receipt

    async def execute(self):
        """
        Gathers recipients for the application.
        Constructs strings to send back to the sender and to those who may hire them.
        Arguments can only be a message to send along with the application, so they do not need to
        be checked for errors like with other commands.
        """

        # Gather recipients
        if self.sender_privilege < Privilege.Admin:
            unlimited_admins = await async_filter(
                Admin,
                room=self.room,
                is_limited=False,
                is_revoked=False
            )

            for adminship in unlimited_admins:
                self.valid_targets += [await async_get(OBUser, adminship=adminship)]

        self.valid_targets = [self.room.owner]

        # Construct strings
        user_suffix = " [Admin]" if self.sender_privilege == Privilege.Admin else ""
        position_prefix = "Unlimited " if self.sender_privilege == Privilege.Admin else ""
        application_message = " ".join(self.args) if self.args else None

        application_body = [
            f"   User: {self.sender}{user_suffix}",
            f"   Position: {position_prefix}Admin",
            f"   Message: {application_message}"
        ]

        self.sender_receipt += (
            # Add an exra newline to separate argument error messages from ban receipt
            [("\n" if self.sender_receipt else "") + "Application sent:"] +
            application_body +
            ["Hopefully the response doesn't start with: \"After careful consideration...\""]
        )

        self.targets_notification += (
            "Application Received" +
            application_body +
            "To hire this user, use /hire."
        )
