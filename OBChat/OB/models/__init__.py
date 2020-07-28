"""
Each of these classes is a model for a database object.
For each model class, there exists a table in the database.
For each attribute of each model class there exists a column in the table (or another table in the
case of ForeignKey, OneToMany, and ManyToMany attributes).

See the Django documentation on Models for more information
https://docs.djangoproject.com/en/3.0/topics/db/models/
"""

from OB.models.admin import Admin
from OB.models.ban import Ban
from OB.models.message import Message
from OB.models.ob_user import OBUser
from OB.models.room import Room
