"""
HireCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_save, async_try_get
from OB.utilities.event import send_system_room_message

class HireCommand(BaseCommand):
    """
    Increases the privilege of an Admin or authenticated user by 1.
    Admins have their adminships un-limited.
    Authenticated users receive a limited adminship.
    """

    async def check_initial_errors(self):
        """
        See BaseCommand.check_initial_errors().
        """

        # Is not an Unlimited Admin
        if self.sender_privilege < Privilege.UnlimitedAdmin:
            self.sender_receipt = [
                "That's a little outside your pay-grade. Only Unlimited Admins may hire admins. "
                "Try to /apply to be Unlimited."
            ]
        # Missing target arguments
        elif len(self.args) == 0:
            self.sender_receipt = ["Usage: /hire <user1> <user2> ..."]

        return not self.sender_receipt

        valid_hires = []
        error_messages = []

        for username in args:
            arg_user = await async_try_get(OBUser, username=username)
            arg_admin = await async_try_get(Admin, user=arg_user)

            # Check for per-argument errors
            if not arg_user:
                error_messages += [
                    f"{username} does not exist. Your imaginary friend needs an account before "
                    "they can be an Admin."
                ]
            elif arg_user == sender:
                error_messages += [
                    "You can't hire yourself. I don't care how good your letter of recommendation is."
                ]
            elif arg_user == room.owner:
                error_messages += ["That's the owner. You know, your BOSS. Nice try."]
            elif not arg_user.is_authenticated or arg_user.is_anon:
                error_messages += [
                    f"{username} hasn't signed up yet. They cannot be trusted with the immense "
                    "responsibility that is adminship."
                ]
            elif arg_admin and not arg_admin.is_limited:
                error_messages += [
                    f"{username} is already an Unlimited Admin. There's nothing left to /hire them "
                    "for."
                ]
            elif arg_admin and sender_privilege < Privilege.Owner:
                error_messages += [
                    f"{username} is already an Admin. Only the owner may promote them to Unlimited "
                    "Admin."
                ]
            else:
                valid_hires += [arg_user]

        send_to_sender = error_messages + [("\n" if error_messages else "") + "Hired:"]
        send_to_targets = ["One or more users have been hired:"] # TODO: Change this to only send when more than one user is hired at once
        send_to_others = ["One or more users have been hired:"]

        for hired_user in valid_hires:
            if arg_admin and sender_privilege == Privilege.Owner:
                # Make the Admin unlimited
                arg_admin.is_limited = False
                await async_save(arg_admin)
            else:
                # Make the user an admin
                await async_save(
                    Admin,
                    user=hired_user,
                    room=room,
                    issuer=sender
                )

            send_to_sender += [f"    {hired_user}"]
            send_to_targets += [f"    {hired_user}"]
            send_to_others += [f"    {hired_user}"]

        if valid_hires:
            send_to_sender += ["Keep an eye on them."]
            await send_system_room_message("\n".join(send_to_sender), room, [sender])

            send_to_targets += ["With great power comes great responsibility."]
            await send_system_room_message("\n".join(send_to_targets), room, valid_hires)

            send_to_others += ["Drinks on them!"]
            await send_system_room_message(
                "\n".join(send_to_others),
                room,
                exclusions=([sender] + valid_hires)
            )
        elif error_messages:
            await send_system_room_message("\n".join(error_messages), room, [sender])
