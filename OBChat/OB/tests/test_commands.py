"""
Tests the command functions (see OB.commands).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from channels.db import database_sync_to_async
from django.contrib.auth import authenticate

from OB.commands.command_handler import handle_command
from OB.constants import ANON_PREFIX, GroupTypes, SYSTEM_USERNAME
from OB.consumers import OBConsumer
from OB.models import Admin, OBUser, Room
from OB.utilities.database import sync_add, sync_delete, sync_get, sync_model_list, sync_save
from OB.utilities.format import get_group_name

async def setup_function():
    """
    Description:
        Sets up database objects required to test the commands.

        This is a built-in pytest fixture that runs before every function.
        See the pytest documentation on xunit-style setup for more information.
        https://docs.pytest.org/en/latest/xunit_setup.html

    Arguments:
        None.

    Return values:
        None.
    """

    await sync_save(
        OBUser,
        username=SYSTEM_USERNAME,
        email="ob-sys@ob.ob",
        password="ob-sys"
    )

    ob_user = await sync_save(
        OBUser,
        username="ob",
        email="ob@ob.ob",
        password="ob"
    )

    obtmf_user = await sync_save(
        OBUser,
        username="obtmf",
        email="obtmf@ob.ob",
        password="obtmf"
    )

    mafdtfafobtmf_user = await sync_save(
        OBUser,
        username="mafdtfafobtmf",
        email="mafdtfafobtmf@ob.ob",
        password="mafdtfafobtmf"
    )

    anon_user = await sync_save(
        OBUser,
        username=f"{ANON_PREFIX}0",
        is_anon=True
    )

    obchat_room = await sync_save(
        Room,
        name="obchat",
        display_name="OBChat",
        owner=ob_user
    )

    await sync_save(
        Room,
        name="obtmfchat",
        display_name="OBTMFChat",
        owner=obtmf_user
    )

    await sync_add(obchat_room.occupants, ob_user)
    await sync_add(obchat_room.occupants, obtmf_user)
    await sync_add(obchat_room.occupants, anon_user)

    await sync_save(
        Admin,
        user=obtmf_user,
        room=obchat_room,
        is_limited=True
    )

    await sync_save(
        Admin,
        user=mafdtfafobtmf_user,
        room=obchat_room
    )

async def teardown_function():
    """
    Description:
        Cleans up the database objects used to test the commands.

        This is a built-in pytest fixture that runs after every function.
        See the pytest documentation on xunit-style setup for more information.
        https://docs.pytest.org/en/latest/xunit_setup.html

    Arguments:
        None.

    Return values:
        None.
    """

    for user in await sync_model_list(OBUser):
        await sync_delete(user)

    for room in await sync_model_list(Room):
        await sync_delete(room)

@mark.asyncio
@mark.django_db()
async def test_user_level():
    """
    Description:
        Tests user-level commands (see OB.commands.user_level).

    Arguments:
        None.

    Return values:
        None.
    """

    ob_user = await sync_get(OBUser, username="ob")
    obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")

    # Test who() errors
    await handle_command("/who knobchat", ob_user, obchat_room)
    await handle_command("/w obtmfchat", ob_user, obchat_room)

    # Test who() correct input
    await handle_command("/w", ob_user, obchat_room)
    await handle_command("/w obchat", ob_user, obchat_room)
    await handle_command("/w obchat obtmfchat", ob_user, obchat_room)

    anon_user = await sync_get(OBUser, username=f"{ANON_PREFIX}0")
    assert await database_sync_to_async(authenticate)(username="ob", password="ob")

    # Test private() errors
    await handle_command("/private", ob_user, obchat_room)
    await handle_command("/p", ob_user, obchat_room)
    await handle_command("/private obtmjeff", ob_user, obchat_room)
    await handle_command("/p /obtmjeff", ob_user, obchat_room)
    await handle_command("/p /obtmf ", ob_user, obchat_room)

    # Test private() correct input
    await handle_command("/private /obtmf What's it like to own OBChat?", ob_user, obchat_room)
    await handle_command("/p /obtmf Must be nice, eh?", ob_user, obchat_room)

    # Test private room creation
    obtmf_user = await sync_get(OBUser, username="obtmf")
    await sync_get(
        Room,
        group_type=GroupTypes.Private,
        name=get_group_name(GroupTypes.Private, ob_user.id, obtmf_user.id)
    )

    # Test create_room() errors
    await handle_command("/room", ob_user, obchat_room)
    await handle_command("/r", ob_user, obchat_room)
    await handle_command("/room anonchat", anon_user, obchat_room)
    await handle_command("/r ob chat", ob_user, obchat_room)
    await handle_command("/r obchat", ob_user, obchat_room)

    # Test create_room() correct input
    await handle_command("/r knobchat", ob_user, obchat_room)

    # Test create_room() success
    await sync_get(Room, group_type=GroupTypes.Room, name="knobchat")

@mark.asyncio
@mark.django_db()
async def test_admin_level():
    """
    Description:
        Tests admin-level commands (see OB.commands.admin_level).

    Arguments:
        None.

    Return values:
        None.
    """

    ob_user = await sync_get(OBUser, username="ob")
    obtmf_user = await sync_get(OBUser, username="obtmf")
    mafdtfafobtmf_user = await sync_get(OBUser, username="mafdtfafobtmf")
    anon_user = await sync_get(OBUser, username=f"{ANON_PREFIX}0")
    obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")

    # Test kick() errors
    await handle_command("/kick", anon_user, obchat_room)
    await handle_command("/k", obtmf_user, obchat_room)
    await handle_command("/k throwbtmf", obtmf_user, obchat_room)
    await handle_command("/k obtmf", obtmf_user, obchat_room)
    await handle_command("/k ob", obtmf_user, obchat_room)
    await handle_command("/k obtmf", mafdtfafobtmf_user, obchat_room)

    # Test kick() correct input
    await handle_command("/kick mafdtfafobtmf", obtmf_user, obchat_room)
    await handle_command(f"/k obtmf {ANON_PREFIX}0", ob_user, obchat_room)

    # Text kick() success
    for occupant in await sync_model_list(obchat_room.occupants):
        assert occupant != obtmf_user
        assert occupant != mafdtfafobtmf_user
        assert occupant != anon_user
