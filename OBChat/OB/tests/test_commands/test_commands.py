"""
Tests the command functions (see OB.commands).
Tests are separated into individual functions so their success/failure can be viewed independently
when using pytest.
To enable pytest assertion rewriting (detailed logs for why assertions failed), ensure that the
module is included in the package's __init__.py (see __init__.py in any of the test packages).

See the pytest documentation on assertion and assertion rewriting for more information.
https://docs.pytest.org/en/stable/assert.html
https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from OB.tests.test_commands.admin_level.ban import BanTest
from OB.tests.test_commands.admin_level.kick import KickTest
from OB.tests.test_commands.admin_level.lift import LiftTest
from OB.tests.test_commands.auth_user_level.apply import ApplyTest
from OB.tests.test_commands.auth_user_level.create import CreateTest
from OB.tests.test_commands.owner_level.delete import DeleteTest
from OB.tests.test_commands.unlimited_admin_level.fire import FireTest
from OB.tests.test_commands.unlimited_admin_level.hire import HireTest
from OB.tests.test_commands.user_level.private import PrivateTest
from OB.tests.test_commands.user_level.who import WhoTest

###################################################################################################
# User Level                                                                                      #
###################################################################################################

@mark.asyncio
@mark.django_db()
async def test_who():
    """
    Tests the /who command function.
    """

    who_test = WhoTest()
    await who_test.run()

@mark.asyncio
@mark.django_db()
async def test_private():
    """
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
    Tests the /create command function.
    """

    create_test = CreateTest()
    await create_test.run()

@mark.asyncio
@mark.django_db()
async def test_apply():
    """
    Tests the /apply command function.
    """

    apply_test = ApplyTest()
    await apply_test.run()

###################################################################################################
# Admin Level                                                                                     #
###################################################################################################

@mark.asyncio
@mark.django_db()
async def test_kick():
    """
    Tests the /kick command function.
    """

    kick_test = KickTest()
    await kick_test.run()

@mark.asyncio
@mark.django_db()
async def test_ban():
    """
    Tests the /ban command function.
    """

    ban_test = BanTest()
    await ban_test.run()

@mark.asyncio
@mark.django_db()
async def test_lift():
    """
    Tests the /lift command function.
    """

    lift_test = LiftTest()
    await lift_test.run()

# TODO: /elevate tests

###################################################################################################
# Unlimited Admin Level                                                                           #
###################################################################################################

@mark.asyncio
@mark.django_db()
async def test_hire():
    """
    Tests the /hire command function.
    """

    hire_test = HireTest()
    await hire_test.run()

@mark.asyncio
@mark.django_db()
async def test_fire():
    """
    Tests the /fire command function.
    """

    fire_test = FireTest()
    await fire_test.run()

###################################################################################################
# Owner Level                                                                                     #
###################################################################################################

@mark.asyncio
@mark.django_db()
async def test_delete():
    """
    Tests the /delete command function.
    """

    delete_test = DeleteTest()
    await delete_test.run()
