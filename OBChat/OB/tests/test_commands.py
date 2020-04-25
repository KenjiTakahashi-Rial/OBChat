"""
Tests the command functions (see OB.commands).

See the Django documentation on Testing for more information.
https://docs.djangoproject.com/en/3.0/topics/testing/
"""

from django.test import Client
from django.test import TestCase
from django.urls import reverse

from OB.commands.user_level import who
from OB.models import OBUser, Room

class TestCommands(TestCase):
    def setUp(self):
        """
        Description:
            Setup phase before every test method. Unfortunately this is overriden from a Django
            TestCase method, so it must be camelCase instead of snake_case like everything else.
            Sets up database objects to test the commands.

        Arguments:
            self (TestCase): A Django TestCase class.

        Return values:
            None
        """

        self.client = Client()

        self.ob_user = OBUser.objects.create_user(
            username="OB",
            email="ob@ob.ob",
            password="ob",
            first_name="Kenji",
            last_name="Takahashi-Rial"
        ).save()

        self.obtmf_user = OBUser.objects.create_user(
            username="OBTMF",
            email="obtmf@ob.ob",
            password="ob",
            first_name="Frank",
            last_name="Jameson"
        ).save()

        self.obchat_room = Room(
            name="obchat",
            display_name="OBChat",
            owner=self.ob_user
        ).save()

        self.obchat_room.occupants.add(self.ob_user)
        self.obchat_room.occupants.add(self.obtmf_user)

    def test_user_level(self):
        """
        Description:
            Tests user-level commands (see OB.commands.user_level).

        Arguments:
            self (TestCase): A Django TestCase class.

        Return values:
            None
        """

        # Test who() errors
        who("obchat knobchat", self.ob_user, self.obchat_room)
        who("", self.ob_user, self.obchat_room)