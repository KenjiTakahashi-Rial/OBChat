"""
Tests the command functions (see OB.commands).

Tests are separated into individual functions so their success/failure can be viewed independently
when using pytest.

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

# TODO: Change all handle_command() calls to be messages sent through the Communicator

from pytest import mark

from OB.tests.test_commands.admin_level import ban, kick
from OB.tests.test_commands.auth_user_level import create_room
from OB.tests.test_commands.user_level import private, who

@mark.asyncio
@mark.django_db()
async def test_who():
    """
    Description:
        Tests the /who command function.
    """

    await who.test_who()

@mark.asyncio
@mark.django_db()
async def test_private():
    """
    Description:
        Tests the /private command function.
    """

    await private.test_private()

@mark.asyncio
@mark.django_db()
async def test_create_room():
    """
    Description:
        Tests the /room command function.
    """

    await create_room.test_create_room()

@mark.asyncio
@mark.django_db()
async def test_kick():
    """
    Description:
        Tests the /kick command function.
    """

    await kick.test_kick()

@mark.asyncio
@mark.django_db()
async def test_ban():
    """
    Description:
        Tests the /ban command function.
    """

    await ban.test_ban()
