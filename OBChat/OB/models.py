"""
Each of these classes is a model for a database object. For each class in this file, there exists a
table in the database.

See the Django documentation on Models for more information
https://docs.djangoproject.com/en/3.0/topics/db/models/
"""

# TODO: Move these into individual modules

from django.db.models import BooleanField, CASCADE, CharField, DateField, DateTimeField, \
    ForeignKey, ManyToManyField, Model, IntegerField, SET_DEFAULT, TextField
from django.contrib.auth.models import AbstractUser

from OB.constants import ANON_PREFIX, GroupTypes

DISPLAY_NAME_MAX_LENGTH = 15
MESSAGE_MAX_LENGTH = 100
ROOM_NAME_MAX_LENGTH = 15
# 40 is the max length of the session_key, which is the suffix of anonymous usernames
ANON_USERNAME_MAX_LENGTH = len(ANON_PREFIX) + 40

class OBUser(AbstractUser):
    """
    Represents a user.
    Authenticated users are saved in the database until they choose to delete their account.
    Unauthenticated (anonymous) users are created automatically when entering a room while not
    logged in, and are deleted automatically when leaving the room.
    Inherits from the AbstractUser superclass, which holds the basic information and handles
    password security.
    """

    display_name = CharField(
        max_length=DISPLAY_NAME_MAX_LENGTH,
        null=True
    )
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
        return "\n".join([
            f"OBUser {{",
            f"    id: {self.id}",
            f"    username: {self.username}",
            f"    display_name: {self.display_name}",
            f"    first_name: {self.first_name}",
            f"    last_name: {self.last_name}",
            f"    birthday: {self.birthday}",
            f"    last_login: {self.last_login}",
            f"    date_joined: {self.date_joined}",
            f"}}"
        ])

class Room(Model):
    """
    Represents a chat room.
    May only be created by authenticated users.
    """

    group_type = IntegerField(
        default=GroupTypes.Room,
        choices=GroupTypes.choices()
    )
    name = CharField(
        max_length=ROOM_NAME_MAX_LENGTH,
        default=None
    )
    display_name = CharField(
        max_length=ROOM_NAME_MAX_LENGTH,
        null=True
    )
    owner = ForeignKey(
        OBUser,
        on_delete=CASCADE,
        related_name="owned_room",
        null=True
    )
    timestamp = DateTimeField(auto_now_add=True)
    is_suspended = BooleanField(default=False)
    occupants = ManyToManyField(
        OBUser,
        related_name="occupied_room"
    )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
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
            occupants += [
                f"    {user}"
            ]
        occupants = "\n".join(occupants) if occupants else None

        return "\n".join([
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
            f"}}"
        ])

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

class Ban(Model):
    """
    Receipt of a user being banned from a room.
    May be lifted to allow a user back in to a room.
    May only be created by a room owner, Unlimited Admin, or Limited Admin.
    """

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
