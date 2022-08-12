"""
Defines the apps within the OBChat project.
"""

from django.apps import AppConfig
from django.db.utils import OperationalError


class OBConfig(AppConfig):
    """
    Defines the OBConfig app within the OBChat project.
    """

    name = "OB"

    def ready(self):
        """
        Clean up occupants and anon OBUsers in the database. The OBConsumer normally handles this,
        but cannot if the server is stopped abruptly.
        This method runs one time when the Django app starts.
        """

        # The Django documentation recommends importing here because you cannot import models at the module-level.
        from OB.models import OBUser, Room

        try:
            # Remove all occupants from all rooms
            for room in Room.objects.all():
                room.occupants.clear()

            # Remove all stray anon users
            for anon_user in OBUser.objects.filter(is_anon=True):
                anon_user.delete()
        except OperationalError as e:  # If the DB hasn't been created yet, these fail
            print(f"WARNING: {e}. Has the DB been created?")
            # TODO: Use a logger instead of print()
