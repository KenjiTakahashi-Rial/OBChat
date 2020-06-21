"""
Defines the Django app within the Django project

See the Django documentation on Applications for more information.
https://docs.djangoproject.com/en/dev/ref/applications/
"""

from django.apps import AppConfig

class OBConfig(AppConfig):
    name = "OB"

    def ready(self):
        """
        Description:
            Clean up occupants and anon OBUsers in the database. The OBConsumer normally handles
            this, but cannot if the server is stopped abruptly.
            This method runs one time when the Django app starts.
        """

        # pylint: disable=import-outside-toplevel
        # Justification: The Django documentation recommends importing here because you cannot
        #   import models at the module-level.
        from OB.models import OBUser, Room

        # Remove all occupants from all rooms
        for room in Room.objects.all():
            room.occupants.clear()

        # Remove all stray anon users
        for anon_user in OBUser.objects.filter(is_anon=True):
            anon_user.delete()
