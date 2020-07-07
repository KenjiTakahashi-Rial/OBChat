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

from OB.tests.test_commands.admin_level.ban import BanTest
from OB.tests.test_commands.admin_level.kick import KickTest
from OB.tests.test_commands.admin_level.lift import LiftTest
from OB.tests.test_commands.auth_user_level.create import CreateTest
from OB.tests.test_commands.user_level.private import PrivateTest
from OB.tests.test_commands.user_level.who import WhoTest

###################################################################################################
# User Level                                                                                      #
###################################################################################################

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

###################################################################################################
# Authenticated User Level                                                                        #
###################################################################################################

@mark.asyncio
@mark.django_db()
async def test_create():
    """
    Description:
        Tests the /create command function.
    """

    create_test = CreateTest()
    await create_test.run()

###################################################################################################
# Admin Level                                                                                     #
###################################################################################################

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
async def test_lift():
    """
    Description:
        Tests the /lift command function.
    """

    lift_test = LiftTest()
    await lift_test.run()
