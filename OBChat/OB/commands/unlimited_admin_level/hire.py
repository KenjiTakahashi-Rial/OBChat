"""
HireCommand class container module.
"""

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, OBUser
from OB.utilities.command import async_get_privilege
from OB.utilities.database import async_save, async_try_get

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
                self.sender_receipt += [
                    f"{username} does not exist. Your imaginary friend needs an account before "
                    "they can be an Admin."
                ]
            # Target user is the sender, themself
            elif arg_user == self.sender:
                self.sender_receipt += [
                    "You can't hire yourself. I don't care how good your letter of recommendation "
                    "is."
                ]
            # Target user is the owner
            elif arg_privilege == Privilege.Owner:
                self.sender_receipt += ["That's the owner. You know, your BOSS. Nice try."]
            # Target user is an anonymous/unauthenticated
            elif not arg_user.is_authenticated or arg_user.is_anon:
                self.sender_receipt += [
                    f"{username} hasn't signed up yet. They cannot be trusted with the immense "
                    "responsibility that is adminship."
                ]
            # Target user is an Unlimited Admin
            elif arg_admin and not arg_admin.is_limited:
                self.sender_receipt += [
                    f"{username} is already an Unlimited Admin. There's nothing left to /hire them "
                    "for."
                ]
            # Sender does not have permission to promote
            elif arg_admin and self.sender_privilege < Privilege.Owner:
                self.sender_receipt += [
                    f"{username} is already an Admin. Only the owner may promote them to Unlimited "
                    "Admin."
                ]
            # Target user is a valid hire
            else:
                self.valid_targets += [arg_user, arg_admin]

        return not self.sender_receipt

    async def execute_implementation(self):
        """
        Add adminships for targets who are not already an Admin.
        Un-limit the adminships for targets who are already an Admin.
        """

        hire_message_body = []

        for hired_user, target_adminship in self.valid_targets:
            if target_adminship and self.sender_privilege == Privilege.Owner:
                # Make the Admin unlimited
                target_adminship.is_limited = False
                await async_save(target_adminship)
            else:
                # Make an adminship for the user
                await async_save(
                    Admin,
                    user=hired_user,
                    room=self.room,
                    issuer=self.sender
                )

            hire_message_body += [f"    {hired_user}"]

        self.sender_receipt += (
            # Add an extra newline to separate argument error messages from fire receipt
            [("\n" if self.sender_receipt else "") + "Hired:"] +
            hire_message_body +
            ["Now for the three month evaluation period."]
        )

        self.occupants_notification += (
            ["One or more users have been hired:"] +
            hire_message_body +
            ["Drinks on them!"]
        )

        self.targets_notification += (
            ["One or more users have been hired:"] +
            hire_message_body +
            ["With great power comes great responsibility."]
        )
