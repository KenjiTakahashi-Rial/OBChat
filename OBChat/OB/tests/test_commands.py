"""
Tests the command functions (see OB.commands).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

# TODO: Change all handle_command() calls to be messages sent through the Communicator
# TODO: Move test functions to separate files and just call them here

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

    OBUser(
        username="throwbtmf",
        email="throwbtmf@ob.ob",
        password="throwbtmf",
        display_name="ThrowBTMF"
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
        is_limited=False
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

    communicators = {}

    try:
        # Database setup
        await database_setup()

        # Get database objects
        ob_user = await sync_get(OBUser, username="ob")
        obtmf_user = await sync_get(OBUser, username="obtmf")
        anon_user_0 = await sync_get(OBUser, username=f"{ANON_PREFIX}0")
        obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")

        # Create a WebsocketCommunicator to test command responses
        communicators["ob"] = await OBCommunicator(
            ob_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        # Test invalid room
        await handle_command("/who knobchat", ob_user, obchat_room)
        correct_response = "knobchat doesn't exist, so that probably means nobody is in there."
        assert await communicators["ob"].receive() == correct_response

        # Test empty room
        await handle_command("/w obtmfchat", ob_user, obchat_room)
        correct_response = "obtmfchat is all empty!"
        assert await communicators["ob"].receive() == correct_response

        # Test no arguments
        await handle_command("/w", ob_user, obchat_room)
        correct_response = "\n".join([
            "Users in obchat:",
            f"    {ob_user} [owner] [you]",
            f"    {obtmf_user} [admin]",
            f"    {anon_user_0}\n"
        ])
        assert await communicators["ob"].receive() == correct_response

        # Test occupied room
        await handle_command("/w obchat", ob_user, obchat_room)
        assert await communicators["ob"].receive() == correct_response

        # Test duplicate room arguments
        await handle_command("/w obchat obchat obchat", ob_user, obchat_room)
        assert await communicators["ob"].receive() == correct_response

        # Test multiple arguments
        await handle_command("/w obchat obtmfchat flobchat", ob_user, obchat_room)
        correct_response = (
            f"{correct_response}\n"
            "obtmfchat is all empty!\n"
            "flobchat doesn't exist, so that probably means nobody is in there."
        )
        assert await communicators["ob"].receive() == correct_response

    finally:
        for communicator in communicators.values():
            await communicator.disconnect()

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

    communicators = {}

    try:
        # Database setup
        await database_setup()

        # Get database objects
        ob_user = await sync_get(OBUser, username="ob")
        obtmf_user = await sync_get(OBUser, username="obtmf")
        obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")

        # Create a WebsocketCommunicator to test command responses
        communicators["ob"] = await OBCommunicator(
            ob_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        # Test no arguments
        await handle_command("/private", ob_user, obchat_room)
        correct_response = "Usage: /private /<user> <message>"
        assert await communicators["ob"].receive() == correct_response

        # Test syntax error
        await handle_command("/p obtmjeff", ob_user, obchat_room)
        correct_response = "Looks like you forgot a \"/\" before the username. I'll let it slide."
        assert await communicators["ob"].receive() == correct_response

        # Test invalid recipient
        await handle_command("/p /obtmjeff", ob_user, obchat_room)
        correct_response = (
            "obtmjeff doesn't exist. Your private message will broadcasted into space instead."
        )
        assert await communicators["ob"].receive() == correct_response

        # Test empty message
        await handle_command("/p /obtmf ", ob_user, obchat_room)
        correct_response = "No message specified. Did you give up at just the username?"
        assert await communicators["ob"].receive() == correct_response

        # Test private room auto-creation
        await handle_command("/p /ob What's it like to own OBChat?", obtmf_user, obchat_room)

        await sync_get(
            Room,
            group_type=GroupTypes.Private,
            name=get_group_name(GroupTypes.Private, ob_user.id, obtmf_user.id)
        )

        # Create WebsocketCommunicators to test private messaging
        communicators["ob_private"] = await OBCommunicator(
            ob_user,
            GroupTypes.Private,
            obtmf_user.username
        ).connect()
        communicators["obtmf_private"] = await OBCommunicator(
            obtmf_user,
            GroupTypes.Private,
            ob_user.username
        ).connect()

        # Test private messaging
        await handle_command("/p /obtmf It's pretty cool.", ob_user, obchat_room)
        correct_response = "It's pretty cool."
        assert (
            await communicators["ob_private"].receive() ==
            await communicators["obtmf_private"].receive() ==
            correct_response
        )

    finally:
        for communicator in communicators.values():
            await communicator.disconnect()

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

    communicators = {}

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
        communicators["ob"] = await OBCommunicator(
            ob_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        communicators["anon"] = await OBCommunicator(
            anon_user_0,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        # Test no arguments
        await handle_command("/room", ob_user, obchat_room)
        correct_response = "Usage: /room <name>"
        assert await communicators["ob"].receive() == correct_response

        # Test unauthenticated user
        await handle_command("/r anonchat", anon_user_0, obchat_room)
        correct_response = "Identify yourself! Must log in to create a room."
        assert await communicators["anon"].receive() == correct_response

        # Test invalid syntax
        await handle_command("/r ob chat", ob_user, obchat_room)
        correct_response = "Room name cannot contain spaces."
        assert await communicators["ob"].receive() == correct_response

        # Test existing room
        await handle_command("/r obchat", ob_user, obchat_room)
        correct_response = "Someone beat you to it. obchat already exists."
        assert await communicators["ob"].receive() == correct_response

        # Test creating room
        await handle_command("/r knobchat", ob_user, obchat_room)
        correct_response = "Sold! Check out your new room: knobchat"
        assert await communicators["ob"].receive() == correct_response
        knobchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="knobchat")

        # Create WebsocketCommunicators to test new room
        communicators["ob_knobchat"] = await OBCommunicator(
            ob_user,
            GroupTypes.Room,
            knobchat_room.name
        ).connect()

        communicators["obtmf_knobchat"] = await OBCommunicator(
            obtmf_user,
            GroupTypes.Room,
            knobchat_room.name
        ).connect()

        communicators["anon_knobchat"] = await OBCommunicator(
            anon_user_1,
            GroupTypes.Room,
            knobchat_room.name
        ).connect()

        # Test new room messaging
        message = "So I heard you made a new room."
        await communicators["obtmf_knobchat"].send(message)
        assert (
            await communicators["ob_knobchat"].receive() ==
            await communicators["obtmf_knobchat"].receive() ==
            await communicators["anon_knobchat"].receive() ==
            message
        )

        message = "You heard right. How's the signal?"
        await communicators["ob_knobchat"].send(message)
        assert (
            await communicators["ob_knobchat"].receive() ==
            await communicators["obtmf_knobchat"].receive() ==
            await communicators["anon_knobchat"].receive() ==
            message
        )

        message = "Can I join in on the fun?"
        await communicators["anon_knobchat"].send(message)
        assert (
            await communicators["ob_knobchat"].receive() ==
            await communicators["obtmf_knobchat"].receive() ==
            await communicators["anon_knobchat"].receive() ==
            message
        )

    finally:
        for communicator in communicators.values():
            await communicator.disconnect()

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

    communicators = {}

    try:
        # Database setup
        await database_setup()

        # Get database objects
        ob_user = await sync_get(OBUser, username="ob")
        obtmf_user = await sync_get(OBUser, username="obtmf")
        mafdtfafobtmf_user = await sync_get(OBUser, username="mafdtfafobtmf")
        throwbtmf_user = await sync_get(OBUser, username="throwbtmf")
        anon_user_0 = await sync_get(OBUser, username=f"{ANON_PREFIX}0")
        obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")

        # Create WebsocketCommunicators to test command responses
        communicators["ob"] = await OBCommunicator(
            ob_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        communicators["obtmf"] = await OBCommunicator(
            obtmf_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        communicators["mafdtfafobtmf"] = await OBCommunicator(
            mafdtfafobtmf_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        communicators["throwbtmf"] = await OBCommunicator(
            throwbtmf_user,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        communicators["anon"] = await OBCommunicator(
            anon_user_0,
            GroupTypes.Room,
            obchat_room.name
        ).connect()

        # Test unauthenticated user
        await handle_command("/kick", anon_user_0, obchat_room)
        correct_response = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "kicking people."
        )
        assert await communicators["anon"].receive() == correct_response

        # Test insufficient privilege
        await handle_command("/k", throwbtmf_user, obchat_room)
        correct_response = (
            "That's a little outside your pay-grade. Only admins may kick users. "
            "Try to /apply to be an admin."
        )
        assert await communicators["throwbtmf"].receive() == correct_response

        # Test no arguments
        await handle_command("/k", mafdtfafobtmf_user, obchat_room)
        correct_response = "Usage: /kick <user1> <user2> ..."
        assert await communicators["mafdtfafobtmf"].receive() == correct_response

        # Test invalid target
        await handle_command("/k showbtmf", mafdtfafobtmf_user, obchat_room)
        correct_response = "Nobody named showbtmf in this room. Are you seeing things?"
        assert await communicators["mafdtfafobtmf"].receive() == correct_response

        # Test self target
        await handle_command("/k mafdtfafobtmf", mafdtfafobtmf_user, obchat_room)
        correct_response = (
            "You can't kick yourself. Just leave the room. Or put yourself on time-out."
        )
        assert await communicators["mafdtfafobtmf"].receive() == correct_response

        # Test owner target
        await handle_command("/k ob", mafdtfafobtmf_user, obchat_room)
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        assert await communicators["mafdtfafobtmf"].receive() == correct_response

        # Test unlimited admin target
        await handle_command("/k obtmf", mafdtfafobtmf_user, obchat_room)
        correct_response = (
            "obtmf is an unlimited admin, so you can't kick them. Please direct all complaints to "
            "your local room owner, I'm sure they'll love some more paperwork to do..."
        )
        assert await communicators["mafdtfafobtmf"].receive() == correct_response

        # Test kick admin
        # await handle_command("/k mafdtfafobtmf", obtmf_user, obchat_room)
        # await handle_command(f"/k obtmf {ANON_PREFIX}0", ob_user, obchat_room)

        # Test kick() success
        # does not exists while testing. Find a way to test this works
        # for occupant in await sync_model_list(obchat_room.occupants):
        #     assert occupant != obtmf_user
        #     assert occupant != mafdtfafobtmf_user
        #     assert occupant != anon_user_0

    finally:
        for communicator in communicators.values():
            await communicator.disconnect()

        await database_teardown()

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
