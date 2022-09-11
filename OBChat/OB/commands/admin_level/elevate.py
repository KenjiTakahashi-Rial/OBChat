"""
ElevateCommand class container module.
"""

from enum import IntEnum
from typing import Optional

from OB.commands.base import BaseCommand
from OB.constants import Privilege
from OB.models import Admin, OBUser, Room
from OB.strings import StringId
from OB.utilities.command import async_get_privilege, is_valid_command
from OB.utilities.database import async_filter, async_model_list, async_try_get


class ElevateCommand(BaseCommand):
    """
    Requests an action (e.g. /kick, /ban, /lift) be performed by a user with higher privilege.
    Can request generally to all users with higher privilege or to a specific user.
    """

    CALLERS: tuple[str, ...] = (StringId.ElevateCaller, StringId.ElevateCallerShort)
    MANUAL: str = StringId.ElevateManual

    def __init__(self, args: list[str], sender: OBUser, room: Room):
        """
        Elevate requires more instance variables than other commands because of its more complex
        syntax.
        """

        super().__init__(args, sender, room)
        self.command: str = ""
        self.message: str = ""
        self.valid_elevations: list[OBUser] = []

    async def check_initial_errors(self) -> bool:
        """
        See BaseCommand.check_initial_errors().
        """

        # Is an anonymous/unauthenticated user
        if self.sender_privilege < Privilege.AuthUser:
            self.sender_receipt += [StringId.AnonElevating]
        # Is authenticated, but not an admin
        elif self.sender_privilege < Privilege.Admin:
            self.sender_receipt += [StringId.NonAdminElevating]
        # Is a valid elevation
        else:
            await self.parse()

        return not self.sender_receipt

    async def parse(self) -> None:
        """
        Parses the arguments into 3 key parts: the command to elevate with its arguments, the target
        usernames to send the elevation request to, and the elevation request message.
        """

        # TODO: Revisit this (there's got to be a better way)
        class Stage(IntEnum):
            """
            Tracks which section of the /elevate command is being parsed in order to organize the
            data.
            """

            Invalid = 0
            Command = 1
            Targets = 2
            Message = 3
            Done = 4

        stage: Stage = Stage.Command

        i: int = 0
        next_stage: bool = False

        while stage < Stage.Done:
            # Check for open parenthesis and valid commands
            if self.args[i][0] != "(" or stage == Stage.Command and not is_valid_command(self.args[0][1:]):
                self.sender_receipt += [StringId.ElevateSyntax]
                return

            while i < len(self.args):
                # There was no end parenthesis
                if i == len(self.args) - 1:
                    self.sender_receipt += [StringId.ElevateSyntax]
                    return

                addition: str = self.args[i]

                # Start parenthesis
                if self.args[i][0] == "(":
                    addition = addition[1:]

                # End parenthesis without command arguments
                if self.args[i][-1] == ")":
                    if i == 1:
                        self.sender_receipt += [StringId.ElevateSyntax]
                        return

                    addition = addition[:-1]
                    next_stage = True

                # Add the argument to the correct instance variable
                if stage == Stage.Command:
                    self.command += addition
                elif stage == Stage.Targets:
                    self.valid_targets += [addition]
                elif stage == Stage.Message:
                    self.message += addition

                i += 1

                if next_stage:
                    stage += 1
                    next_stage = False

    async def check_arguments(self) -> bool:
        """
        See BaseCommand.check_arguments().
        """

        if not self.valid_targets:
            # Get all users with higher privilege
            if self.sender_privilege < Privilege.UnlimitedAdmin:
                unlimited_admins = await async_filter(Admin, room=self.room, is_limited=False)
                self.valid_elevations += unlimited_admins
            self.valid_elevations += [self.room.owner]
        else:
            # Check for per-argument errors
            for username in self.valid_targets:
                arg_user: Optional[OBUser] = await async_try_get(OBUser, username=username)
                arg_privilege: Privilege = Privilege.Invalid

                if arg_user:
                    arg_privilege = await async_get_privilege(arg_user, self.room)

                if not arg_user or arg_user not in await async_model_list(self.room.occupants):
                    self.sender_receipt += [StringId.UserNotPresent.format(username)]
                elif arg_user == self.sender:
                    self.sender_receipt += [StringId.ElevateSelf]
                elif arg_privilege < Privilege.UnlimitedAdmin:
                    self.sender_receipt += [StringId.ElevatePeer.format(username)]
                else:
                    self.valid_elevations += [arg_user]

        return bool(self.valid_elevations)

    async def execute_implementation(self) -> None:
        """
        Construct an elevation request message and send it to the valid elevations.
        Also send a receipt to the sender.
        """

        # Construction the elevation request
        elevate_message_body: list[str] = [
            f"    {StringId.Recipients}" + ", ".join(self.valid_elevations),
            f"    {StringId.CommandRequested} {self.command}",
            f"    {StringId.Message} {self.message if self.message else None}",
        ]

        self.sender_receipt += (
            # Add an extra newline to separate argument error messages from request receipt
            [("\n" if self.sender_receipt else "") + StringId.ElevateSenderReceiptPreface]
            + elevate_message_body
        )

        self.targets_notification += [
            StringId.ElevateTargetsNotificationPreface.format(self.sender)
        ] + elevate_message_body
