"""
Tests the command functions (see OB.commands).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

# TODO: Change all handle_command() calls to be messages sent through the Communicator

from channels.db import database_sync_to_async

from pytest import mark

from OB.commands.command_handler import handle_command
from OB.communicators import OBCommunicator
from OB.constants import ANON_PREFIX, GroupTypes, SYSTEM_USERNAME
from OB.models import Admin, OBUser, Room
from OB.utilities.database import sync_get
from OB.utilities.format import get_group_name

@database_sync_to_async
def database_setup():
    """
    Description:
        Sets up database objects required to test the commands.
        The built-in pytest setup fixture causes threading issues with the asynchronous command
        testing.
    """

    OBUser(
        username=SYSTEM_USERNAME,
        email="ob-sys@ob.ob",
        password="ob-sys"
    ).save()

    ob_user = OBUser(
        username="ob",
        email="ob@ob.ob",
        password="ob",
        display_name="OB"
    ).save()

    obtmf_user = OBUser(
        username="obtmf",
        email="obtmf@ob.ob",
        password="obtmf",
        display_name="OBTMF"
    ).save()

    mafdtfafobtmf_user = OBUser(
        username="mafdtfafobtmf",
        email="mafdtfafobtmf@ob.ob",
        password="mafdtfafobtmf",
        display_name="MAFDTFAFOBTMF"
    ).save()

    anon_user_0_0 = OBUser(
        username=f"{ANON_PREFIX}0",
        is_anon=True
    ).save()

    OBUser(
        username=f"{ANON_PREFIX}1",
        is_anon=True
    ).save()

    obchat_room = Room(
        name="obchat",
        display_name="OBChat",
        owner=ob_user
    ).save()

    Room(
        name="obtmfchat",
        display_name="OBTMFChat",
        owner=obtmf_user
    ).save()

    obchat_room.occupants.add(ob_user)
    obchat_room.occupants.add(obtmf_user)
    obchat_room.occupants.add(anon_user_0_0)

    Admin(
        user=obtmf_user,
        room=obchat_room,
        issuer=ob_user,
        is_limited=True
    ).save()

    Admin(
        user=mafdtfafobtmf_user,
        room=obchat_room,
        issuer=ob_user
    ).save()

@database_sync_to_async
def database_teardown():
    """
    Description:
        Cleans up the database objects used to test the commands.
        The built-in pytest teardown fixture causes threading issues with the asynchronous command
        testing.
    """

    for user_object in OBUser.objects.all():
        user_object.delete()

    for room_object in Room.objects.all():
        room_object.delete()

@mark.asyncio
@mark.django_db()
async def test_who():
    """
    Description:
        Tests the /who command (see OB.commands.user_level.who()).
        Wrapped in a try block to prevent following tests from failing their database setup if this
        test fails before cleaning up the database.
        Normally, the built-in pytest teardown_function() accounts for this, but it is not used
        for testing commands (see database_teardown()).
    """

    ob_communicator = None

    try:
        # Database setup
        await database_setup()

        # Get database objects
        ob_user = await sync_get(OBUser, username="ob")
        obtmf_user = await sync_get(OBUser, username="obtmf")
        anon_user_0 = await sync_get(OBUser, username=f"{ANON_PREFIX}0")
        obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")

        # Create a WebsocketCommunicator to test command responses
        ob_communicator = await OBCommunicator(
            ob_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        # Test invalid room
        await handle_command("/who knobchat", ob_user, obchat_room)
        correct_response = "knobchat doesn't exist, so that probably means nobody is in there."
        assert await ob_communicator.receive() == correct_response

        # Test empty room
        await handle_command("/w obtmfchat", ob_user, obchat_room)
        correct_response = "obtmfchat is all empty!"
        assert await ob_communicator.receive() == correct_response

        # Test no arguments
        await handle_command("/w", ob_user, obchat_room)
        correct_response = "\n".join([
            "Users in obchat:",
            f"    {ob_user} [owner] [you]",
            f"    {obtmf_user} [admin]",
            f"    {anon_user_0}\n"
        ])
        assert await ob_communicator.receive() == correct_response

        # Test occupied room
        await handle_command("/w obchat", ob_user, obchat_room)
        assert await ob_communicator.receive() == correct_response

        # Test duplicate room arguments
        await handle_command("/w obchat obchat obchat", ob_user, obchat_room)
        assert await ob_communicator.receive() == correct_response

        # Test multiple arguments
        await handle_command("/w obchat obtmfchat flobchat", ob_user, obchat_room)
        correct_response = (
            f"{correct_response}\n"
            "obtmfchat is all empty!\n"
            "flobchat doesn't exist, so that probably means nobody is in there."
        )
        assert await ob_communicator.receive() == correct_response

    finally:
        if ob_communicator:
            await ob_communicator.disconnect()

        await database_teardown()

@mark.asyncio
@mark.django_db()
async def test_private():
    """
    Description:
        Tests the /private command (see OB.commands.user_level.private()).
        Wrapped in a try block to prevent following tests from failing their database setup if this
        test fails before cleaning up the database.
        Normally, the built-in pytest teardown_function() accounts for this, but it is not used
        for testing commands (see database_teardown()).
    """

    ob_communicator = None
    ob_private_communicator = None
    obtmf_private_communicator = None

    try:
        # Database setup
        await database_setup()

        # Get database objects
        ob_user = await sync_get(OBUser, username="ob")
        obtmf_user = await sync_get(OBUser, username="obtmf")
        obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")

        # Create a WebsocketCommunicator to test command responses
        ob_communicator = await OBCommunicator(
            ob_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        # Test no arguments
        await handle_command("/private", ob_user, obchat_room)
        correct_response = "Usage: /private /<user> <message>"
        assert await ob_communicator.receive() == correct_response

        # Test syntax error
        await handle_command("/p obtmjeff", ob_user, obchat_room)
        correct_response = "Looks like you forgot a \"/\" before the username. I'll let it slide."
        assert await ob_communicator.receive() == correct_response

        # Test invalid recipient
        await handle_command("/p /obtmjeff", ob_user, obchat_room)
        correct_response = ("obtmjeff doesn't exist. Your private message will broadcasted into "
                            "space instead.")
        assert await ob_communicator.receive() == correct_response

        # Test empty message
        await handle_command("/p /obtmf ", ob_user, obchat_room)
        correct_response = ("No message specified. Did you give up at just the username?")
        assert await ob_communicator.receive() == correct_response

        # Test private room auto-creation
        await handle_command("/p /ob What's it like to own OBChat?", obtmf_user, obchat_room)

        await sync_get(
            Room,
            group_type=GroupTypes.Private,
            name=get_group_name(GroupTypes.Private, ob_user.id, obtmf_user.id)
        )

        # Create WebsocketCommunicators to test private messaging
        ob_private_communicator = await OBCommunicator(
            ob_user,
            GroupTypes.Private,
            obtmf_user.username
        ).connect()
        obtmf_private_communicator = await OBCommunicator(
            obtmf_user,
            GroupTypes.Private,
            ob_user.username
        ).connect()

        # Test private messaging
        await handle_command("/p /obtmf It's pretty cool.", ob_user, obchat_room)
        correct_response = ("It's pretty cool.")
        assert (
            await ob_private_communicator.receive() ==
            await obtmf_private_communicator.receive() ==
            correct_response
        )

    finally:
        if ob_communicator:
            await ob_communicator.disconnect()
        if ob_private_communicator:
            await ob_private_communicator.disconnect()
        if obtmf_private_communicator:
            await obtmf_private_communicator.disconnect()

        await database_teardown()

@mark.asyncio
@mark.django_db()
async def test_create_room():
    """
    Description:
        Tests the /room command (see OB.commands.user_level.create_room()).
        Wrapped in a try block to prevent following tests from failing their database setup if this
        test fails before cleaning up the database.
        Normally, the built-in pytest teardown_function() accounts for this, but it is not used
        for testing commands (see database_teardown()).
    """

    ob_communicator = None
    anon_communicator = None
    ob_knobchat_communicator = None
    obtmf_knobchat_communicator = None
    anon_knobchat_communicator = None

    try:
        # Database setup
        await database_setup()

        # Get database objects
        ob_user = await sync_get(OBUser, username="ob")
        obtmf_user = await sync_get(OBUser, username="obtmf")
        anon_user_0 = await sync_get(OBUser, username=f"{ANON_PREFIX}0")
        anon_user_1 = await sync_get(OBUser, username=f"{ANON_PREFIX}1")
        obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")

        # Create WebsocketCommunicators to test command responses
        ob_communicator = await OBCommunicator(
            ob_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        anon_communicator = await OBCommunicator(
            anon_user_0,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        # Test no arguments
        await handle_command("/room", ob_user, obchat_room)
        correct_response = "Usage: /room <name>"
        assert await ob_communicator.receive() == correct_response

        # Test unauthenticated user
        await handle_command("/r anonchat", anon_user_0, obchat_room)
        correct_response = "Identify yourself! Must log in to create a room."
        assert await anon_communicator.receive() == correct_response

        # Test invalid syntax
        await handle_command("/r ob chat", ob_user, obchat_room)
        correct_response = "Room name cannot contain spaces."
        assert await ob_communicator.receive() == correct_response

        # Test existing room
        await handle_command("/r obchat", ob_user, obchat_room)
        correct_response = "Someone beat you to it. obchat already exists."
        assert await ob_communicator.receive() == correct_response

        # Test creating room
        await handle_command("/r knobchat", ob_user, obchat_room)
        correct_response = "Sold! Check out your new room: knobchat"
        assert await ob_communicator.receive() == correct_response
        knobchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="knobchat")

        # Create WebsocketCommunicators to test new room
        ob_knobchat_communicator = await OBCommunicator(
            ob_user,
            GroupTypes.Room,
            knobchat_room.name
        ).connect()

        obtmf_knobchat_communicator = await OBCommunicator(
            obtmf_user,
            GroupTypes.Room,
            knobchat_room.name
        ).connect()

        anon_knobchat_communicator = await OBCommunicator(
            anon_user_1,
            GroupTypes.Room,
            knobchat_room.name
        ).connect()

        # Test new room messaging
        message = "So I heard you made a new room."
        await obtmf_knobchat_communicator.send(message)
        assert (
            await ob_knobchat_communicator.receive() ==
            await obtmf_knobchat_communicator.receive() ==
            await anon_knobchat_communicator.receive() ==
            message
        )

        message = "You heard right. How's the signal?"
        await ob_knobchat_communicator.send(message)
        assert (
            await ob_knobchat_communicator.receive() ==
            await obtmf_knobchat_communicator.receive() ==
            await anon_knobchat_communicator.receive() ==
            message
        )

        message = "Can I join in on the fun?"
        await anon_knobchat_communicator.send(message)
        assert (
            await ob_knobchat_communicator.receive() ==
            await obtmf_knobchat_communicator.receive() ==
            await anon_knobchat_communicator.receive() ==
            message
        )

    finally:
        if ob_communicator:
            await ob_communicator.disconnect()
        if anon_communicator:
            await anon_communicator.disconnect()
        if ob_knobchat_communicator:
            await ob_knobchat_communicator.disconnect()
        if obtmf_knobchat_communicator:
            await obtmf_knobchat_communicator.disconnect()
        if anon_knobchat_communicator:
            await anon_knobchat_communicator.disconnect()

        await database_teardown()

@mark.asyncio
@mark.django_db()
async def test_kick():
    """
    Description:
        Tests the /kick command (see OB.commands.kick()).
        Wrapped in a try block to prevent following tests from failing their database setup if this
        test fails before cleaning up the database.
        Normally, the built-in pytest teardown_function() accounts for this, but it is not used
        for testing commands (see database_teardown()).
    """

    try:
        await database_setup()

        ob_user = await sync_get(OBUser, username="ob")
        obtmf_user = await sync_get(OBUser, username="obtmf")
        mafdtfafobtmf_user = await sync_get(OBUser, username="mafdtfafobtmf")
        anon_user_0 = await sync_get(OBUser, username=f"{ANON_PREFIX}0")
        obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")

        # Test kick() errors
        await handle_command("/kick", anon_user_0, obchat_room)
        await handle_command("/k", obtmf_user, obchat_room)
        await handle_command("/k throwbtmf", obtmf_user, obchat_room)
        await handle_command("/k obtmf", obtmf_user, obchat_room)
        await handle_command("/k ob", obtmf_user, obchat_room)
        await handle_command("/k obtmf", mafdtfafobtmf_user, obchat_room)

        # Test kick() correct input
        await handle_command("/kick mafdtfafobtmf", obtmf_user, obchat_room)
        await handle_command(f"/k obtmf {ANON_PREFIX}0", ob_user, obchat_room)

        # Test kick() success
        # TODO: kick() test does not remove occupants because that code lies in OBConsumer, which
        # does not exists while testing. Find a way to test this works
        # for occupant in await sync_model_list(obchat_room.occupants):
        #     assert occupant != obtmf_user
        #     assert occupant != mafdtfafobtmf_user
        #     assert occupant != anon_user_0

        # TODO: Add ban() tests

    finally:
        await database_teardown()
