"""
Useful session functions.

See the Django documentation on Sessions for more information.
https://docs.djangoproject.com/en/3.0/topics/http/sessions/
"""

from channels.db import database_sync_to_async

@database_sync_to_async
def async_cycle_key(session):
    """
    Description:
        Allows an asynchronous function to change a session's key.

    Arguments:
        session (Session): The Django Session to cycle the key for.
    """

    session.cycle_key()
