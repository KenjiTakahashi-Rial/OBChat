"""
KickCommand class container module
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_model_list, async_try_get
from OB.utilities.event import send_room_event

class KickCommand(BaseCommand):
    """
    Remove one or more OBConsumers from the group a Room is associated with.
    Kicked users will not receive messages from the group until they rejoin the Room.
    """

    # TODO: Add an option to do this silently (without notifying everyone)

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticted user
        if self.sender_privilege < Privilege.AuthUser:
            self.sender_receipt = [
                "You're not even logged in! Try making an account first, then we can talk about "
                "kicking people."
            ]
        # Is authenticated, but not an admin
        elif self.sender_privilege < Privilege.Admin:
            self.sender_receipt = [
                "That's a little outside your pay-grade. Only admins may kick users. Try to "
                "/apply to be an Admin."
            ]
        # Missing target arguments
        elif not self.args:
            self.sender_receipt = ["Usage: /kick <user1> <user2> ..."]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_initial_errors().
        """

        for username in self.args:
            arg_user = await async_try_get(OBUser, username=username)

            if arg_user:
                arg_privilege = await async_get_privilege(arg_user, self.room)

            # Target user is not present in the room
            if not arg_user or arg_user not in await async_model_list(self.room.occupants):
                self.sender_receipt += [
                    f"Nobody named {username} in this room. Are you seeing things?"
                ]
            # Target user is the sender
            elif arg_user == self.sender:
                self.sender_receipt += [
                    f"You can't kick yourself. Just leave the room. Or put yourself on time-out."
                ]
            # Target user is the owner
            elif arg_privilege == Privilege.Owner:
                self.sender_receipt += [f"That's the owner. You know, your BOSS. Nice try."]
            # Target user has Privilege greater than or equal to the sender
            elif arg_privilege >= self.sender_privilege:
                job_title = "Admin"

                if arg_privilege == self.sender_privilege:
                    job_title += " just like you"

                if arg_privilege == Privilege.UnlimitedAdmin:
                    job_title = "Unlimited " + job_title

                self.sender_receipt += [
                    f"{arg_user} is an {job_title}, so you can't kick them. Feel free to "
                    "/elevate your complaints to someone who has more authority."
                ]
            else:
                self.valid_targets += [arg_user]

        return bool(self.valid_targets)

    async def execute_implementation(self):
        """
        Kick users from the room.
        Constructs strings to send back to the sender and to the other occupants of the room.
        The sender receipt includes per-argument error messages.
        """

        kick_message_body = []

        for kicked_user in self.valid_targets:
            # Kick the user
            kick_event = {
                "type": "kick",
                "target_id": kicked_user.id
            }
            await send_room_event(self.room.id, kick_event)

            # Notify others that a user was kicked
            kick_message_body += [f"   {kicked_user}"]

        self.sender_receipt += (
            # Add an exra newline to separate argument error messages from ban receipt
            [("\n" if self.sender_receipt else "") + "Kicked:"] +
            kick_message_body +
            ["That'll show them."]
        )
        self.occupants_notification += (
            ["One or more users have been kicked:"] +
            kick_message_body +
            ["Let this be a lesson to you all."]
        )
