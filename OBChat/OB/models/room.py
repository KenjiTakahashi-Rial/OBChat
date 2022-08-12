"""
Room class container module.
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

from OB.constants import GroupTypes
from OB.models.ob_user import OBUser

ROOM_NAME_MAX_LENGTH = 15


class Room(Model):
    """
    Represents a chat room.
    May only be created by authenticated users.
    """

    group_type = IntegerField(default=GroupTypes.Room, choices=GroupTypes.choices())
    name = CharField(max_length=ROOM_NAME_MAX_LENGTH, default=None)
    display_name = CharField(max_length=ROOM_NAME_MAX_LENGTH, null=True)
    owner = ForeignKey(OBUser, on_delete=CASCADE, related_name="owned_room", null=True)
    timestamp = DateTimeField(auto_now_add=True)
    is_suspended = BooleanField(default=False)
    occupants = ManyToManyField(OBUser, related_name="occupied_room")

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

    def __str__(self, show_id=False, show_owner=False):
        if self.display_name:
            display_string = f"{self.display_name} ({self.name})"
        else:
            display_string = self.name

        if show_id:
            display_string += f"[{self.id}]"

        if show_owner:
            display_string += f", owned by {self.owner}"

        return display_string

    def __repr__(self):
        occupants = []
        for user in self.occupants:
            occupants += [f"    {user}"]
        occupants = "\n".join(occupants) if occupants else None

        return "\n".join(
            [
                f"Room {{",
                f"    group_type: {self.group_type}",
                f"    name: {self.name}",
                f"    display_name: {self.display_name}",
                f"    owner: {self.owner}",
                f"    timestamp: {self.timestamp}",
                f"    is_suspended: {self.is_suspended}",
                f"    occupants: {{",
                f"    {occupants}",
                f"    }}",
                f"}}",
            ]
        )
