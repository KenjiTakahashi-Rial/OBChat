"""
Tests the command functions (see OB.commands).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

import pytest

from OB.commands.user_level import who
from OB.constants import SYSTEM_USERNAME
from OB.models import OBUser, Room
from OB.utilities.database import sync_add, sync_get, sync_save

@pytest.mark.asyncio
@pytest.mark.django_db()
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

@pytest.mark.asyncio
@pytest.mark.django_db()
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
