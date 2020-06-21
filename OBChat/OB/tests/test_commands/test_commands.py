"""
Tests the command functions (see OB.commands).

Tests are separated into individual functions so their success/failure can be viewed independently
when using pytest.

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html

To enable pytest assertion rewriting (detailed logs for why assertions failed), ensure that the
module is included in the package's __init__.py (see __init__.py in any of the test packages).

See the pytest documentation on assertion and assertion rewriting for more information.
https://docs.pytest.org/en/stable/assert.html
https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting
"""

from pytest import mark

from OB.tests.test_commands.admin_level import ban, kick, lift_ban
from OB.tests.test_commands.auth_user_level import create_room
from OB.tests.test_commands.user_level import private, who

@mark.asyncio
@mark.django_db()
async def test_who():
    """
    Description:
        Tests the /who command function.
    """

    who_test = who.WhoTest()
    await who_test.run()

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

@mark.asyncio
@mark.django_db()
async def test_lift_ban():
    """
    Description:
        Tests the /lift command function.
    """

    await lift_ban.test_lift_ban()
