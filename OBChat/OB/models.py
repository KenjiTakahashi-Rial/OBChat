"""
Each of these classes is a model for a database object. For each class in this file, there exists a
table in the database.

See the Django documentation on Models for more information
https://docs.djangoproject.com/en/3.0/topics/db/models/
"""

from django.db.models import BooleanField, CASCADE, CharField, DateField, DateTimeField, \
    ForeignKey, ManyToManyField, Model, IntegerField, TextField
from django.contrib.auth.models import AbstractUser

from OB.constants import ANON_PREFIX, GroupTypes

DISPLAY_NAME_MAX_LENGTH = 15
MESSAGE_MAX_LENGTH = 100
ROOM_NAME_MAX_LENGTH = 15
# 40 is the max length of the session_key, which is the suffix of anonymous usernames
ANON_USERNAME_MAX_LENGTH = len(ANON_PREFIX) + 40

class OBUser(AbstractUser):
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
        return ("\nOBUser {\n"
                f"   id: {self.id}\n"
                f"   username: {self.username}\n"
                f"   display_name: {self.display_name}\n"
                f"   first_name: {self.first_name}\n"
                f"   last_name: {self.last_name}\n"
                f"   birthday: {self.birthday}\n"
                f"   last_login: {self.last_login}\n"
                f"   date_joined: {self.date_joined}\n"
                "}\n")

class Room(Model):
    group_type = IntegerField(default=GroupTypes.Room, choices=GroupTypes.choices())
    name = CharField(max_length=ROOM_NAME_MAX_LENGTH, default=0)
    display_name = CharField(max_length=ROOM_NAME_MAX_LENGTH, null=True)
    owner = ForeignKey(OBUser, on_delete=CASCADE, related_name="owned_room", null=True)
    timestamp = DateTimeField(auto_now_add=True)
    is_suspended = BooleanField(default=False)
    occupants = ManyToManyField(OBUser, related_name="occupied_room")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
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
        return ("\nRoom {\n"
                f"   group_type: {self.group_type}\n"
                f"   name: {self.name}\n"
                f"   display_name: {self.display_name}\n"
                f"   owner: {self.owner}\n"
                f"   timestamp: {self.timestamp}\n"
                f"   is_suspended: {self.is_suspended}\n"
                f"   occupants: {self.occupants}\n"
                "}\n")

class Admin(Model):
    user = ForeignKey(OBUser, on_delete=CASCADE, default=0)
    room = ForeignKey(Room, on_delete=CASCADE, default=0)
    is_limited = BooleanField(default=True)
    is_revoked = BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
        return self

    def __str__(self, show_id=False):
        display_string = f"{self.user}, admin of {self.room.name}"

        if show_id:
            display_string += f"[{self.id}]"

        return display_string

    def __repr__(self):
        return ("\nAdmin {\n"
                f"   user: {self.user}\n"
                f"   room: {self.room}\n"
                f"   is_limited: {self.is_limited}\n"
                f"   is_revoked: {self.is_revoked}\n"
                "}\n")

class Ban(Model):
    user = ForeignKey(OBUser, on_delete=CASCADE, default=0)
    room = ForeignKey(Room, on_delete=CASCADE, default=0)
    timestamp = DateTimeField(auto_now_add=True)
    is_lifted = BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
        return self

    def __str__(self, show_id=False):
        display_string = f"{self.user}, banned in {self.room}"

        if self.is_lifted:
            display_string += "(lifted)"

        if show_id:
            display_string += f"[{self.id}]"

        return display_string

    def __repr__(self):
        return ("\nBan {\n"
                f"   user: {self.user}\n"
                f"   room: {self.room}\n"
                f"   timestamp: {self.timestamp}\n"
                f"   is_lifted: {self.is_lifted}\n"
                "}\n")

class Message(Model):
    message = TextField(max_length=MESSAGE_MAX_LENGTH)
    sender = ForeignKey(OBUser, on_delete=CASCADE, default=0, null=True)
    anon_username = CharField(
        max_length=ANON_USERNAME_MAX_LENGTH,
        default=None,
        null=True
    )
    room = ForeignKey(Room, on_delete=CASCADE, default=0)
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
        return ("\nMessage {\n"
                f"   message: {self.message}\n"
                f"   sender: {self.sender}\n"
                f"   anon_username: {self.anon_username}\n"
                f"   room: {self.room}\n"
                f"   timestamp: {self.rotimestampom}\n"
                f"   is_edited: {self.is_edited}\n"
                f"   is_deleted: {self.is_deleted}\n"
                "}\n")
