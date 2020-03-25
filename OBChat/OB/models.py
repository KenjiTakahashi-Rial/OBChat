from django.db import models
from django.contrib.auth.models import User
from .constants import DISPLAY_NAME_MAX_LENGTH, ROOM_NAME_MAX_LENGTH, MESSAGE_MAX_LENGTH


class OBUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    display_name = models.CharField(max_length=DISPLAY_NAME_MAX_LENGTH, null=True)
    birthday = models.DateField(null=True)
    is_expelled = models.BooleanField(default=False)
    is_ob = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Room(models.Model):
    name = models.CharField(max_length=ROOM_NAME_MAX_LENGTH, default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_suspended = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default=0)
    # admin must apply to an unlimited admin to make/remove limited admins
    is_limited = models.BooleanField(default=True)
    is_revoked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}:{self.room.name}"


class Ban(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_lifted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}:{self.room.name}"


class Message(models.Model):
    message = models.TextField(max_length=MESSAGE_MAX_LENGTH)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.message
