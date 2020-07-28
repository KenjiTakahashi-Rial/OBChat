"""
Each of these classes is a model for a database object. For each class in this file, there exists a
table in the database.

See the Django documentation on Models for more information
https://docs.djangoproject.com/en/3.0/topics/db/models/
"""

from django.db.models import BooleanField, CASCADE, CharField, DateField, DateTimeField, \
    ForeignKey, ManyToManyField, Model, IntegerField, SET_DEFAULT, TextField
from django.contrib.auth.models import AbstractUser

from OB.constants import ANON_PREFIX, GroupTypes

DISPLAY_NAME_MAX_LENGTH = 15
MESSAGE_MAX_LENGTH = 100
ROOM_NAME_MAX_LENGTH = 15
# 40 is the max length of the session_key, which is the suffix of anonymous usernames
ANON_USERNAME_MAX_LENGTH = len(ANON_PREFIX) + 40

class Ban(Model):
    """
    Receipt of a user being banned from a room.
    May be lifted to allow a user back in to a room.
    May only be created by a room owner, Unlimited Admin, or Limited Admin.
    """

    # TODO: Add support for timed bans

    user = ForeignKey(
        OBUser,
        on_delete=CASCADE,
        default=-1
    )
    room = ForeignKey(
        Room,
        on_delete=CASCADE,
        default=-1
    )
    issuer = ForeignKey(
        OBUser,
        related_name="ban_issued",
        on_delete=SET_DEFAULT,
        default=-1
    )
    timestamp = DateTimeField(auto_now_add=True)
    is_lifted = BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
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
        return "\n".join([
            f"Ban {{",
            f"    user: {self.user}",
            f"    room: {self.room}",
            f"    issuer: {self.issuer}",
            f"    timestamp: {self.timestamp}",
            f"    is_lifted: {self.is_lifted}",
            f"}}"
        ])

class Message(Model):
    """
    Messages sent in a room.
    Includes private and system messages.
    May be created by any user.
    """

    message = TextField(max_length=MESSAGE_MAX_LENGTH)
    sender = ForeignKey(
        OBUser,
        related_name="message_sent",
        on_delete=CASCADE,
        null=True
    )
    recipients = ManyToManyField(
        OBUser,
        related_name="message_received",
        default=None
    )
    exclusions = ManyToManyField(
        OBUser,
        related_name="message_excluded",
        default=None
    )
    anon_username = CharField(
        max_length=ANON_USERNAME_MAX_LENGTH,
        default=None,
        null=True
    )
    room = ForeignKey(
        Room,
        on_delete=CASCADE,
        default=-1
    )
    timestamp = DateTimeField(auto_now_add=True)
    is_edited = BooleanField(default=False)
    is_deleted = BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
        return self

    def __str__(self, show_id=False):
        display_string = f"\"{self.message}\" from {self.sender or self.anon_username}"

        if show_id:
            display_string += f"[{self.id}]"

        return display_string

    def __repr__(self):
        recipients = []
        for user in self.recipients:
            recipients += [
                f"    {user}"
            ]
        recipients = "\n".join(recipients) if recipients else None

        exclusions = []
        for user in self.exclusions:
            exclusions += [
                f"    {user}"
            ]
        exclusions = "\n".join(exclusions) if exclusions else None

        return "\n".join([
            f"Message {{",
            f"    message: {self.message}",
            f"    sender: {self.sender}",
            f"    recipients: {{",
            f"    {recipients}",
            f"    }}"
            f"    exclusions: {{",
            f"    {exclusions}",
            f"    }}"
            f"    anon_username: {self.anon_username}",
            f"    room: {self.room}",
            f"    timestamp: {self.timestamp}",
            f"    is_edited: {self.is_edited}",
            f"    is_deleted: {self.is_deleted}",
            f"}}"
        ])
