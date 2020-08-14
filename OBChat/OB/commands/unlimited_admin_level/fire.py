"""
FireCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_delete, async_save, async_try_get
from OB.utilities.event import send_system_room_message

class FireCommand(BaseCommand):
    """
    Removes one or more existing Admin database objects.
    The user may no longer issue admin-level commands in the target room.
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is not an Unlimited Admin
        if self.sender_privilege < Privilege.UnlimitedAdmin:
            self.sender_receipt = [
                "That's a little outside your pay-grade. Only Unlimited Admins may fire admins. "
                "Try to /apply to be Unlimited."
            ]
        # Missing target arguments
        elif len(self.args) == 0:
            self.sender_receipt = ["Usage: /fire <user1> <user2> ..."]

        return not self.sender_receipt

    async def check_arguments(self):
        """
        See BaseCommand.check_arguments().
        """

        for username in self.args:
            arg_user = await async_try_get(OBUser, username=username)

            if arg_user:
                arg_privilege = await async_get_privilege(arg_user, self.room)
                arg_admin = await async_try_get(Admin, user=arg_user, room=self.room)

            # Target user does not exist
            if not arg_user:
                self.sender_receipt += [f"{username} does not exist. You can't fire a ghost... can you?"]
            # Target user is the sender, themself
            elif arg_user == self.sender:
                self.sender_receipt += [
                    "You can't fire yourself. I don't care how bad your performance reviews are."
                ]
            # Target user is the owner
            elif arg_privilege == Privilege.Owner:
                self.sender_receipt += ["That's the owner. You know, your BOSS. Nice try."]
            # Target user is not an Admin
            elif not arg_admin:
                self.sender_receipt += [
                    f"{username} is just a regular ol' user, so you can't fire them. You can /kick or "
                    "/ban them if you want."
                ]
            # Target user has higher privilege than sender
            elif not arg_admin.is_limited and self.sender_privilege < Privilege.Owner:
                self.sender_receipt += [
                    f"{username} is an Unlimited Admin, so you can't fire them. Please direct all "
                    "complaints to your local room owner, I'm sure they'll love some more paperwork to"
                    " do..."
                ]
            # Target user is a valid fire
            else:
                self.valid_targets += [{"user": arg_user, "adminship": arg_admin}]

            return bool(self.valid_targets)

        send_to_sender = self.sender_receipt + [("\n" if self.sender_receipt else "") + "Fired:"]
        send_to_targets = ["One or more users have been fired:"] # TODO: Change this to only send when more than one user is fired at once
        send_to_others = ["One or more users have been fired:"]

        for fired_user in valid_fires:
            if fired_user["adminship"].is_limited:
                # Remove the adminship
                await async_delete(fired_user["adminship"])
            else:
                # Make the adminship limited
                fired_user["adminship"].is_limited = True
                await async_save(fired_user["adminship"])

            send_to_sender += [f"    {fired_user}"]
            send_to_targets += [f"    {fired_user}"]
            send_to_others += [f"    {fired_user}"]

        if valid_fires:
            send_to_sender += ["It had to be done."]
            await send_system_room_message("\n".join(send_to_sender), room, [sender])

            send_to_targets += ["Clean out your desk."]
            await send_system_room_message("\n".join(send_to_sender), room, valid_fires)

            send_to_others += ["Those budget cuts are killer."]
            await send_system_room_message(
                "\n".join(send_to_others),
                room,
                exclusions=([sender] + valid_fires)
            )
        elif error_messages:
            await send_system_room_message("\n".join(error_messages), room, [sender])
