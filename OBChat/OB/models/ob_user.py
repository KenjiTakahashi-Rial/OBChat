"""
OBUser class container module.
"""

from django.contrib.auth.models import AbstractUser
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

DISPLAY_NAME_MAX_LENGTH = 15


class OBUser(AbstractUser):
    """
    Represents a user.
    Authenticated users are saved in the database until they choose to delete their account.
    Unauthenticated (anonymous) users are created automatically when entering a room while not
    logged in, and are deleted automatically when leaving the room.
    Inherits from the AbstractUser superclass, which holds the basic information and handles
    password security.
    """

    display_name = CharField(max_length=DISPLAY_NAME_MAX_LENGTH, null=True)
    birthday = DateField(null=True)
    is_anon = BooleanField(default=False)
    is_expelled = BooleanField(default=False)
    is_ob = BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        return self

    def __str__(self, show_id=False):
        if self.display_name:
            display_string = f"{self.display_name} ({self.username})"
        else:
            display_string = self.username

        if show_id:
            display_string += f"[{self.id}]"

        return display_string

    def __repr__(self):
        return "\n".join(
            [
                f"OBUser {{",
                f"    id: {self.id}",
                f"    username: {self.username}",
                f"    display_name: {self.display_name}",
                f"    first_name: {self.first_name}",
                f"    last_name: {self.last_name}",
                f"    birthday: {self.birthday}",
                f"    last_login: {self.last_login}",
                f"    date_joined: {self.date_joined}",
                f"}}",
            ]
        )
