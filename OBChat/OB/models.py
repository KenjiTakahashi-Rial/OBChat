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

    def __str__(self):
        if self.display_name:
            name_string = f"{self.display_name} ({self.username})"
        else:
            name_string = self.username

        return f"{name_string} [{self.id}]"

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

    def __str__(self):
        if self.display_name:
            name_string = f"{self.display_name} ({self.name})"
        else:
            name_string = self.name

        return f"{name_string} [{self.id}], owned by {self.owner}"

class Admin(Model):
    user = ForeignKey(OBUser, on_delete=CASCADE, default=0)
    room = ForeignKey(Room, on_delete=CASCADE, default=0)
    # admin must apply to an unlimited admin to promote/demote limited admins
    is_limited = BooleanField(default=True)
    is_revoked = BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
        return self

    def __str__(self):
        return f"{self.user}, admin of {self.room.name} [{self.id}]"

class Ban(Model):
    user = ForeignKey(OBUser, on_delete=CASCADE, default=0)
    room = ForeignKey(Room, on_delete=CASCADE, default=0)
    timestamp = DateTimeField(auto_now_add=True)
    is_lifted = BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
        return self

    def __str__(self):
        lifted_string = " (lifted)" if self.is_lifted else ""
        return f"{self.user}, banned in {self.room} {lifted_string} [{self.id}]"

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

    def __str__(self):
        if self.sender:
            return f"{self.message} from {self.sender} [{self.id}]"

        return f"{self.message} from {self.anon_username} [{self.id}]"
