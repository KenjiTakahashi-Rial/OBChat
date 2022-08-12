"""
Ban class container module.
"""

from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    DateField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    Model,
    IntegerField,
    SET_DEFAULT,
    TextField,
)

from OB.models.ob_user import OBUser
from OB.models.room import Room


class Ban(Model):
    """
    Receipt of a user being banned from a room.
    May be lifted to allow a user back in to a room.
    May only be created by a room owner, Unlimited Admin, or Limited Admin.
    """

    # TODO: Add support for timed bans

    user = ForeignKey(OBUser, on_delete=CASCADE, default=-1)
    room = ForeignKey(Room, on_delete=CASCADE, default=-1)
    issuer = ForeignKey(
        OBUser, related_name="ban_issued", on_delete=SET_DEFAULT, default=-1
    )
    timestamp = DateTimeField(auto_now_add=True)
    is_lifted = BooleanField(default=False)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
        return self

    def __str__(self, show_id=False):
        display_string = f"{self.user}, banned in {self.room}"

        if self.is_lifted:
            display_string += "(lifted)"

        if show_id:
            display_string += f"[{self.id}]"

        return display_string

    def __repr__(self):
        return "\n".join(
            [
                f"Ban {{",
                f"    user: {self.user}",
                f"    room: {self.room}",
                f"    issuer: {self.issuer}",
                f"    timestamp: {self.timestamp}",
                f"    is_lifted: {self.is_lifted}",
                f"}}",
            ]
        )
