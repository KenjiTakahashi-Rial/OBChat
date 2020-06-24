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

from OB.tests.test_commands.admin_level import ban, lift_ban
from OB.tests.test_commands.admin_level.ban import BanTest
from OB.tests.test_commands.admin_level.kick import KickTest
from OB.tests.test_commands.auth_user_level.room import RoomTest
from OB.tests.test_commands.user_level.private import PrivateTest
from OB.tests.test_commands.user_level.who import WhoTest

@mark.asyncio
@mark.django_db()
async def test_who():
    """
    Description:
        Tests the /who command function.
    """

    who_test = WhoTest()
    await who_test.run()

@mark.asyncio
@mark.django_db()
async def test_private():
    """
    Description:
        Tests the /private command function.
    """

    private_test = PrivateTest()
    await private_test.run()

@mark.asyncio
@mark.django_db()
async def test_create_room():
    """
    Description:
        Tests the /room command function.
    """

    room_test = RoomTest()
    await room_test.run()

@mark.asyncio
@mark.django_db()
async def test_kick():
    """
    Description:
        Tests the /kick command function.
    """

    kick_test = KickTest()
    await kick_test.run()

@mark.asyncio
@mark.django_db()
async def test_ban():
    """
    Description:
        Tests the /ban command function.
    """

    ban_test = BanTest()
    await ban_test.run()

@mark.asyncio
@mark.django_db()
async def test_lift_ban():
    """
    Description:
        Tests the /lift command function.
    """

    await lift_ban.test_lift_ban()
