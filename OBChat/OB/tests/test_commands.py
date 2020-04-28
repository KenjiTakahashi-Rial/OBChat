"""
Tests the command functions (see OB.commands).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from channels.db import database_sync_to_async
from django.contrib.auth import authenticate

from OB.commands.user_level import create_room, who
from OB.constants import ANON_PREFIX, SYSTEM_USERNAME
from OB.models import OBUser, Room
from OB.utilities.database import sync_add, sync_get, sync_save

async def database_setup():
    """
    Description:
        Sets up database objects required to test the commands.

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

    await sync_save(
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

    await database_setup()

    ob_user = await sync_get(OBUser, username="ob")
    obchat_room = await sync_get(Room, name="obchat")

    # Test who() errors
    await who("knobchat", ob_user, obchat_room)
    await who("obtmfchat", ob_user, obchat_room)

    # Test who() correct input
    await who("obchat", ob_user, obchat_room)
    await who("obchat obtmfchat", ob_user, obchat_room)

    anon_user = await sync_get(OBUser, username=f"{ANON_PREFIX}0")
    assert await database_sync_to_async(authenticate)(username="ob", password="ob")

    # Test create_room() errors
    await create_room("", ob_user, obchat_room)
    await create_room("anonchat", anon_user, obchat_room)
    await create_room("ob chat", ob_user, obchat_room)
    await create_room("obchat", ob_user, obchat_room)

    # Test create_room() correct input
    await create_room("knobchat", ob_user, obchat_room)

    # Test create_room() success
    await sync_get(Room, name="knobchat")
