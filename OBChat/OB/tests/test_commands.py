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
from OB.models import Admin, Ban, Message, OBUser, Room
from OB.utilities.database import async_get, async_model_list
from OB.utilities.format import get_group_name

@database_sync_to_async
def database_setup():
    """
    Description:
        Sets up database objects required to test the commands.
        Ideally, the return value would be a dict of OBUsers and Rooms, but returning any database
        objects from this function will cause threading issues by locking the database.
        The built-in pytest setup fixture causes threading issues with the asynchronous command
        testing.
    """

    OBUser(
        username=SYSTEM_USERNAME,
        email="ob-sys@ob.ob",
        password="ob-sys"
    ).save()

    owner = OBUser(
        username="owner",
        email="owner@ob.ob",
        password="owner",
        display_name="Owner"
    ).save()

    unlimited_admin_0 = OBUser(
        username="unlimited_admin_0",
        email="unlimited_admin_0@ob.ob",
        password="unlimited_admin",
        display_name="UnlimitedAdmin0"
    ).save()

    unlimited_admin_1 = OBUser(
        username="unlimited_admin_1",
        email="unlimited_admin_1@ob.ob",
        password="unlimited_admin_1",
        display_name="UnlimitedAdmin1"
    ).save()

    limited_admin_0 = OBUser(
        username="limited_admin_0",
        email="limited_admin_0@ob.ob",
        password="limited_admin_0",
        display_name="LimitedAdmin0"
    ).save()

    limited_admin_1 = OBUser(
        username="limited_admin_1",
        email="limited_admin_1@ob.ob",
        password="limited_admin_1",
        display_name="LimitedAdmin1"
    ).save()

    auth_user = OBUser(
        username="auth_user",
        email="auth_user@ob.ob",
        password="auth_user",
        display_name="AuthUser"
    ).save()

    anon_0 = OBUser(
        username=f"{ANON_PREFIX}0",
        is_anon=True
    ).save()

    OBUser(
        username=f"{ANON_PREFIX}1",
        is_anon=True
    ).save()

    room_0 = Room(
        name="room_0",
        display_name="Room0",
        owner=owner
    ).save()

    Room(
        name="empty_room",
        display_name="EmptyRoom",
        owner=unlimited_admin_0
    ).save()

    add_occupants(
        room_0,
        [
            owner,
            unlimited_admin_0,
            unlimited_admin_1,
            limited_admin_0,
            limited_admin_1,
            auth_user,
            anon_0
        ]
    )

    Admin(
        user=unlimited_admin_0,
        room=room_0,
        issuer=owner,
        is_limited=False
    ).save()

    Admin(
        user=unlimited_admin_1,
        room=room_0,
        issuer=owner,
        is_limited=False
    ).save()

    Admin(
        user=limited_admin_0,
        room=room_0,
        issuer=owner
    ).save()

    Admin(
        user=limited_admin_1,
        room=room_0,
        issuer=owner
    ).save()

@database_sync_to_async
def database_teardown():
    """
    Description:
        Cleans up the database objects used to test the commands.
        The built-in pytest teardown fixture causes threading issues with the asynchronous command
        testing.
    """

    for admin in Admin.objects.all():
        admin.delete()

    for ban in Ban.objects.all():
        ban.delete()

    for message in Message.objects.all():
        message.delete()

    for ob_user in OBUser.objects.all():
        ob_user.delete()

    for room in Room.objects.all():
        room.delete()

def add_occupants(room, occupants):
    """
    Description:
        Adds a list of users to the occupants of room if they are not already in it.

    Arguments:
        room (Room): The room to add users to the occupants of.
        occupants (list[OBUser]): The list of users to add to the room's occupants list.
    """

    for user in occupants:
        if user not in room.occupants.all():
            room.occupants.add(user)

@database_sync_to_async
def async_add_occupants(room, occupants):
    """
    Description:
        Allows an asynchronous function to add a list of users to the occupants of room if they are
        not already in it.

    Arguments:
        room (Room): The room to add users to the occupants of.
        occupants (list[OBUser]): The list of users to add to the room's occupants list.
    """

    add_occupants(room, occupants)

async def communicator_setup(room):
    """
    Description:
        Sets up the communicator objects used to test the commands.
        The built-in pytest setup fixture causes threading issues with the asynchronous command
        testing.

    Arguments:
        room (Room): The room to get a dict of communicators for.

    Return values:
        Returns a dict of communicators for each user occupying the room argument.
        The keys are the usernames of the occupants.
    """

    communicators = {}

    for user in await async_model_list(room.occupants):
        communicators[user.username] = await OBCommunicator(
            user,
            GroupTypes.Room,
            room.name
        ).connect()

    return communicators

async def communicator_teardown(communicators):
    """
    Description:
        Cleans up the communicator objects used to test the commands.
        The built-in pytest teardown fixture causes threading issues with the asynchronous command
        testing.

    Arguments:
        communicators (dict{string: OBCommunicator}): The dict of communicators to clean up.
    """

    if not communicators:
        return

    for communicator in communicators.values():
        try:
            await communicator.disconnect()
        except AttributeError:
            # The commnicator has already been disconnected
            # OB.consumers.disconnect() raises an AttributeError because OBConsumer.room is None
            pass


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

    communicators = None

    try:
        # Database setup
        await database_setup()

        # Get database objects
        owner = await async_get(OBUser, username="owner")
        unlimited_admin_0 = await async_get(OBUser, username="unlimited_admin_0")
        unlimited_admin_1 = await async_get(OBUser, username="unlimited_admin_1")
        limited_admin_0 = await async_get(OBUser, username="limited_admin_0")
        limited_admin_1 = await async_get(OBUser, username="limited_admin_1")
        auth_user = await async_get(OBUser, username="auth_user")
        anon_0 = await async_get(OBUser, username=f"{ANON_PREFIX}0")
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test nonexistent room error
        await handle_command("/who nonexistent_room", owner, room_0)
        correct_response = (
            "nonexistent_room doesn't exist, so that probably means nobody is in there."
        )
        assert await communicators["owner"].receive() == correct_response

        # Test empty room error
        await handle_command("/w empty_room", owner, room_0)
        correct_response = "empty_room is all empty!"
        assert await communicators["owner"].receive() == correct_response

        # Test current room with no argument
        await handle_command("/w", owner, room_0)
        correct_response = "\n".join([
            "Users in room_0:",
            f"    {owner} [owner] [you]",
            f"    {unlimited_admin_0} [admin]",
            f"    {unlimited_admin_1} [admin]",
            f"    {limited_admin_0} [admin]",
            f"    {limited_admin_1} [admin]",
            f"    {auth_user}",
            f"    {anon_0}\n"
        ])
        assert await communicators["owner"].receive() == correct_response

        # Test current room with explicit argument
        await handle_command("/w room_0", owner, room_0)
        assert await communicators["owner"].receive() == correct_response

        # Test duplicate room arguments
        await handle_command("/w room_0 room_0 room_0", owner, room_0)
        assert await communicators["owner"].receive() == correct_response

        # Test multiple arguments
        await handle_command("/w room_0 empty_room nonexistent_room", owner, room_0)
        correct_response = (
            f"{correct_response}\n"
            "empty_room is all empty!\n"
            "nonexistent_room doesn't exist, so that probably means nobody is in there."
        )
        assert await communicators["owner"].receive() == correct_response

    finally:
        await communicator_teardown(communicators)
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

    communicators = None

    try:
        # Database setup
        await database_setup()

        # Get database objects
        owner = await async_get(OBUser, username="owner")
        unlimited_admin_0 = await async_get(OBUser, username="unlimited_admin_0")
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test no arguments error
        await handle_command("/private", owner, room_0)
        correct_response = "Usage: /private /<user> <message>"
        assert await communicators["owner"].receive() == correct_response

        # Test missing "/" error
        await handle_command("/p no_slash", owner, room_0)
        correct_response = "Looks like you forgot a \"/\" before the username. I'll let it slide."
        assert await communicators["owner"].receive() == correct_response

        # Test nonexistent recipient error
        await handle_command("/p /nonexistent_user", owner, room_0)
        correct_response = (
            "nonexistent_user doesn't exist. Your private message will broadcasted into space "
            "instead."
        )
        assert await communicators["owner"].receive() == correct_response

        # Test empty message error
        await handle_command("/p /unlimited_admin_0", owner, room_0)
        correct_response = "No message specified. Did you give up at just the username?"
        assert await communicators["owner"].receive() == correct_response

        # Test private room auto-creation
        await handle_command("/p /owner What's it like to own room_0?", unlimited_admin_0, room_0)

        await async_get(
            Room,
            group_type=GroupTypes.Private,
            name=get_group_name(GroupTypes.Private, owner.id, unlimited_admin_0.id)
        )

        # Create WebsocketCommunicators to test private messaging
        communicators["owner_private"] = await OBCommunicator(
            owner,
            GroupTypes.Private,
            unlimited_admin_0.username
        ).connect()
        communicators["unlimited_admin_0_private"] = await OBCommunicator(
            unlimited_admin_0,
            GroupTypes.Private,
            owner.username
        ).connect()

        # Test private messaging
        await handle_command("/p /unlimited_admin_0 It's pretty cool.", owner, room_0)
        correct_response = "It's pretty cool."
        assert (
            await communicators["owner_private"].receive() ==
            await communicators["unlimited_admin_0_private"].receive() ==
            correct_response
        )

    finally:
        await communicator_teardown(communicators)
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

    communicators = None

    try:
        # Database setup
        await database_setup()

        # Get database objects
        owner = await async_get(OBUser, username="owner")
        unlimited_admin_0 = await async_get(OBUser, username="unlimited_admin_0")
        anon_0 = await async_get(OBUser, username=f"{ANON_PREFIX}0")
        anon_1 = await async_get(OBUser, username=f"{ANON_PREFIX}1")
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test no arguments error
        await handle_command("/room", owner, room_0)
        correct_response = "Usage: /room <name>"
        assert await communicators["owner"].receive() == correct_response

        # Test unauthenticated user error
        await handle_command("/r anon_room", anon_0, room_0)
        correct_response = "Identify yourself! Must log in to create a room."
        assert await communicators[f"{ANON_PREFIX}0"].receive() == correct_response

        # Test multiple arguments error
        await handle_command("/r room 1", owner, room_0)
        correct_response = "Room name cannot contain spaces."
        assert await communicators["owner"].receive() == correct_response

        # Test existing room error
        await handle_command("/r room_0", owner, room_0)
        correct_response = "Someone beat you to it. room_0 already exists."
        assert await communicators["owner"].receive() == correct_response

        # Test room creation
        await handle_command("/r room_1", owner, room_0)
        correct_response = "Sold! Check out your new room: room_1"
        assert await communicators["owner"].receive() == correct_response
        room_1 = await async_get(Room, group_type=GroupTypes.Room, name="room_1")

        # Create WebsocketCommunicators to test new room
        communicators["owner_room_1"] = await OBCommunicator(
            owner,
            GroupTypes.Room,
            room_1.name
        ).connect()

        communicators["unlimited_admin_0_room_1"] = await OBCommunicator(
            unlimited_admin_0,
            GroupTypes.Room,
            room_1.name
        ).connect()

        communicators["anon_room_1"] = await OBCommunicator(
            anon_1,
            GroupTypes.Room,
            room_1.name
        ).connect()

        # Test new room messaging
        message = "So I heard you made a new room."
        await communicators["unlimited_admin_0_room_1"].send(message)
        assert (
            await communicators["owner_room_1"].receive() ==
            await communicators["unlimited_admin_0_room_1"].receive() ==
            await communicators["anon_room_1"].receive() ==
            message
        )

        message = "You heard right. How's the signal?"
        await communicators["owner_room_1"].send(message)
        assert (
            await communicators["owner_room_1"].receive() ==
            await communicators["unlimited_admin_0_room_1"].receive() ==
            await communicators["anon_room_1"].receive() ==
            message
        )

        message = "Can I join in on the fun?"
        await communicators["anon_room_1"].send(message)
        assert (
            await communicators["owner_room_1"].receive() ==
            await communicators["unlimited_admin_0_room_1"].receive() ==
            await communicators["anon_room_1"].receive() ==
            message
        )

    finally:
        await communicator_teardown(communicators)
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

    communicators = None

    try:
        # Database setup
        await database_setup()

        # Get database objects
        owner = await async_get(OBUser, username="owner")
        unlimited_admin_0 = await async_get(OBUser, username="unlimited_admin_0")
        limited_admin_0 = await async_get(OBUser, username="limited_admin_0")
        auth_user = await async_get(OBUser, username="auth_user")
        anon_0 = await async_get(OBUser, username=f"{ANON_PREFIX}0")
        room_0 = await async_get(Room, group_type=GroupTypes.Room, name="room_0")
        occupants = await async_model_list(room_0.occupants)

        # Communicator setup
        communicators = await communicator_setup(room_0)

        # Test unauthenticated user kicking error
        await handle_command("/kick", anon_0, room_0)
        correct_response = (
            "You're not even logged in! Try making an account first, then we can talk about "
            "kicking people."
        )
        assert await communicators[f"{ANON_PREFIX}0"].receive() == correct_response

        # Test authenticated user kicking error
        await handle_command("/k", auth_user, room_0)
        correct_response = (
            "That's a little outside your pay-grade. Only admins may kick users. "
            "Try to /apply to be an admin."
        )
        assert await communicators["auth_user"].receive() == correct_response

        # Test no arguments error
        await handle_command("/k", limited_admin_0, room_0)
        correct_response = "Usage: /kick <user1> <user2> ..."
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test absent target error
        await handle_command("/k auth_user_1", limited_admin_0, room_0)
        correct_response = "Nobody named auth_user_1 in this room. Are you seeing things?"
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test self target error
        await handle_command("/k limited_admin_0", limited_admin_0, room_0)
        correct_response = (
            "You can't kick yourself. Just leave the room. Or put yourself on time-out."
        )
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking owner error
        await handle_command("/k owner", limited_admin_0, room_0)
        correct_response = "That's the owner. You know, your BOSS. Nice try."
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking unlimited admin error
        await handle_command("/k unlimited_admin_0", limited_admin_0, room_0)
        correct_response = (
            "unlimited_admin_0 is an unlimited admin, so you can't kick them. Please direct all "
            "complaints to your local room owner, I'm sure they'll love some more paperwork to "
            "do..."
        )
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking limited admin error
        await handle_command("/k limited_admin_1", limited_admin_0, room_0)
        correct_response = (
            "limited_admin_1 is an admin just like you, so you can't kick them. Please direct all "
            "complaints to your local room owner, I'm sure they'll love some more paperwork to "
            "do..."
        )
        assert await communicators["limited_admin_0"].receive() == correct_response

        # Test limited admin kicking authenticated user
        await handle_command("/k auth_user", limited_admin_0, room_0)
        sender_response = (
            "Kicked:\n"
            f"   auth_user\n"
            "That'll show them."
        )
        others_response = (
            "One or more users have been kicked:\n"
            f"   auth_user\n"
            "Let this be a lesson to you all."
        )
        assert auth_user not in await async_model_list(room_0.occupants)
        assert await communicators["limited_admin_0"].receive() == sender_response
        assert (
            await communicators["owner"].receive() ==
            await communicators["unlimited_admin_0"].receive() ==
            await communicators["unlimited_admin_1"].receive() ==
            await communicators["limited_admin_0"].receive() ==
            await communicators["limited_admin_1"].receive() ==
            await communicators[f"{ANON_PREFIX}0"].receive() ==
            others_response
        )
        assert (await communicators["auth_user"].receive())["refresh"]
        assert (await communicators["auth_user"].receive_output())["type"] == "websocket.close"

        # Add kicked users back to room occupants

        # await handle_command(f"/k obtmf {ANON_PREFIX}0", owner, room_0)

    finally:
        await communicator_teardown(communicators)
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
