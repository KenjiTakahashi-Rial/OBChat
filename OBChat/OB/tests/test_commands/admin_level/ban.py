"""
Tests the /ban command function (see OB.commands.admin_level.ban()).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.commands.command_handler import handle_command
from OB.constants import ANON_PREFIX, GroupTypes
from OB.models import OBUser, Room
from OB.utilities.test import communicator_setup, communicator_teardown, database_setup, \
    database_teardown
from OB.utilities.database import async_add_occupants, async_get, async_model_list, async_save

@mark.asyncio
@mark.django_db()
async def test_ban():
    """
    Description:
        Tests the /ban command (see OB.commands.ban()).
        Wrapped in a try block to prevent following tests from failing their database setup if this
        test fails before cleaning up the database.
        Normally, the built-in pytest teardown_function() accounts for this, but it is not used
        for testing commands (see database_teardown()).
    """

    # TODO: Implement this
