"""
Admin class container module.
"""

from django.db.models import BooleanField, CASCADE, CharField, DateField, DateTimeField, \
    ForeignKey, ManyToManyField, Model, IntegerField, SET_DEFAULT, TextField

from OB.models.ob_user import OBUser
from OB.models.room import Room

class Admin(Model):
    """
    Receipt of an adminship given to a user for a room.
    Starts as Limited Admin, which has fewer privileges than Unlimited Admin.
    May only be created by a room owner or Unlimited Admin.
    """

    user = ForeignKey(
        OBUser,
        on_delete=CASCADE,
        default=-1,
        related_name="adminship"
    )
    room = ForeignKey(
        Room,
        on_delete=CASCADE,
        default=-1
    )
    issuer = ForeignKey(
        OBUser,
        related_name="admin_hired",
        on_delete=SET_DEFAULT,
        default=-1
    )
    is_limited = BooleanField(default=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )
        return self

    def __str__(self, show_id=False):
        display_string = f"{self.user}, Admin of {self.room.name}"

        if show_id:
            display_string += f"[{self.id}]"

        return display_string

    def __repr__(self):
        return "\n".join([
            f"Admin {{",
            f"    user: {self.user}",
            f"    room: {self.room}",
            f"    issuer: {self.issuer}",
            f"    is_limited: {self.is_limited}",
            f"}}"
        ])
