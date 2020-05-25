"""
Storage for session functions that are called in multiple places and are not associated with any
particular instance of a class.

See the Django documentation on Sessions for more information.
https://docs.djangoproject.com/en/3.0/topics/http/sessions/
"""

from channels.db import database_sync_to_async

@database_sync_to_async
def sync_cycle_key(session):
    """
    Description:
        Allows an asynchronous function to change a session's key.

    Arguments:
        session (Session): The Django Session to cycle the key for.
    """

    session.cycle_key()
