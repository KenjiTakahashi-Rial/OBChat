"""
Models import organizer module. Holds all models classes to simplify models import statements.
Each of these classes is a model for a database object.
For each class in this file, there exists a table in the database.

See the Django documentation on Models for more information
https://docs.djangoproject.com/en/3.0/topics/db/models/
"""

# pylint: disable=unused-import
# Justification: The purpose of this module is simply to hold imports.

from OB.models.admin import Admin
from OB.models.ban import Ban
from OB.models.message import Message
from OB.models.ob_user import OBUser
from OB.models.room import Room
