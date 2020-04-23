"""
Each of these classes is a model for a database object. For each class in this file, there exists a
table in the database.

See the Django documentation on Models for more information
https://docs.djangoproject.com/en/3.0/topics/db/models/
"""

from django.db.models import BooleanField, CASCADE, CharField, DateField, DateTimeField, \
    ForeignKey, ManyToManyField, Model, TextField
from django.contrib.auth.models import AbstractUser

DISPLAY_NAME_MAX_LENGTH = 15
MESSAGE_MAX_LENGTH = 100
ROOM_NAME_MAX_LENGTH = 15

class OBUser(AbstractUser):
    display_name = CharField(max_length=DISPLAY_NAME_MAX_LENGTH, null=True)
    birthday = DateField(null=True)
    is_expelled = BooleanField(default=False)
    is_ob = BooleanField(default=False)

    def __str__(self):
        if self.display_name:
            name_string = f"{self.display_name} ({self.username})"
        else:
            name_string = f"{self.username}"

        return f"<OBUser: {name_string}>"

# TODO: Add a display name and if the user tries to make the room with caps in the name, make that
# the display name and the lowercase the name
class Room(Model):
    name = CharField(max_length=ROOM_NAME_MAX_LENGTH, default=0)
    owner = ForeignKey(OBUser, on_delete=CASCADE, default=0, related_name="owned_room")
    timestamp = DateTimeField(auto_now_add=True)
    is_suspended = BooleanField(default=False)
    occupants = ManyToManyField(OBUser, related_name="occupied_room")

    def __str__(self):
        return f"<Room: {self.name} owned by {self.owner}>"

class Admin(Model):
    user = ForeignKey(OBUser, on_delete=CASCADE, default=0)
    room = ForeignKey(Room, on_delete=CASCADE, default=0)
    # admin must apply to an unlimited admin to promote/demote limited admins
    is_limited = BooleanField(default=True)
    is_revoked = BooleanField(default=False)

    def __str__(self):
        return f"<Admin: {self.user} admin of {self.room.name}>"

class Ban(Model):
    user = ForeignKey(OBUser, on_delete=CASCADE, default=0)
    room = ForeignKey(Room, on_delete=CASCADE, default=0)
    timestamp = DateTimeField(auto_now_add=True)
    is_lifted = BooleanField(default=False)

    def __str__(self):
        lifted_string = " (lifted)" if self.is_lifted else ""
        return f"<Ban: {self.user} banned in {self.room}{lifted_string}>"

class Message(Model):
    message = TextField(max_length=MESSAGE_MAX_LENGTH)
    sender = ForeignKey(OBUser, on_delete=CASCADE, default=0)
    room = ForeignKey(Room, on_delete=CASCADE, default=0)
    timestamp = DateTimeField(auto_now_add=True)
    is_edited = BooleanField(default=False)
    is_deleted = BooleanField(default=False)

    def __str__(self):
        return f"<Message: {self.message} from {self.sender}>"
