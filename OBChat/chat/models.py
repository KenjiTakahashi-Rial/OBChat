from django.db import models
from .constants import *


class User(models.Model):
    name = models.CharField(max_length=USERNAME_MAX_LENGTH)
    timestamp = models.DateTimeField()
    is_super = models.BooleanField(False)
    is_ob = models.BooleanField(False)
    is_expelled = models.BooleanField(False)

class Room(models.Model):
    name = models.CharField(max_length=ROOM_NAME_MAX_LENGTH)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField()
    is_suspended = models.BooleanField(False)

class Admin(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    is_limited = models.BooleanField(True) # admin must appeal to an unlimited admin or the owner to ban a user
    is_revoked = models.BooleanField(False)

class Ban(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    timestamp = models.DateTimeField()
    is_lifted = models.BooleanField(False)

class Message(models.Model):
    message = models.TextField(max_length=MESSAGE_MAX_LENGTH)
    room = models.IntegerField()
    sender = models.IntegerField()
    timestamp = models.DateTimeField()
    is_edited = models.BooleanField(False)
    is_deleted = models.BooleanField(False)