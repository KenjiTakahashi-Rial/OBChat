"""
Tests the command functions (see OB.commands).

See the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

import json

from types import SimpleNamespace

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from django.conf.urls import url
from django.contrib.auth import authenticate

from pytest import mark

from OB.commands.command_handler import handle_command
from OB.constants import ANON_PREFIX, GroupTypes, SYSTEM_USERNAME
from OB.consumers import OBConsumer
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

    anon_user = OBUser(
        username=f"{ANON_PREFIX}0",
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
    obchat_room.occupants.add(anon_user)

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
async def communicator_setup(user, group_type, url_arg):
    """
    Description:
        Sets up the communicator object required to test the commands.
        Gives a placeholder "session" key for the scope because OBConsumer uses a session key to
        generate anonymous usernames.
        Communicator objects are used to test Consumers.

        See the Django Channels documentation on Testing for more information.
        https://channels.readthedocs.io/en/latest/topics/testing.html

    Arguments:
        user (OBUser): The user who will be assigned to the communicator's self.user.
        group_type (GroupType): Determines which type of group the communicator will connect to.
        url_arg (string): Either a room name or a username, depending on the group type. Additional
            information to connect to the correct group.
    """

    if group_type == GroupTypes.Room:
        application = URLRouter([
            url(r"^chat/(?P<room_name>[-\w]+)/$", OBConsumer)
        ])
        communicator = WebsocketCommunicator(application, f"/chat/{url_arg}/")
    elif group_type == GroupTypes.Private:
        application = URLRouter([
            url(r"^private/(?P<username>[-\w]+)/$", OBConsumer)
        ])
        communicator = WebsocketCommunicator(application, f"/private/{url_arg}/")
    else:
        raise TypeError("communicator_setup() received an invalid GroupType.")

    communicator.scope["user"] = user
    communicator.scope["session"] = SimpleNamespace(session_key=8)

    is_connected, subprotocol = await communicator.connect()

    assert is_connected
    assert not subprotocol

    return communicator

async def communicator_teardown(communicator):
    """
    Description:
        Cleans up the communicator object used to test the commands.
        Communicator objects are used to test Consumers.

        See the Django Channels documentation on Testing for more information.
        https://channels.readthedocs.io/en/latest/topics/testing.html

    Arguments:
        communicator (WebsocketCommunicator): The communicator used to test the commands. Should
            originate from consumer_setup().
    """

    await communicator.disconnect()

@mark.asyncio
@mark.django_db()
async def test_user_level():
    """
    Description:
        Tests user-level commands (see OB.commands.user_level).
        Wrapped in a try block to prevent following tests from failing their database setup if this
        test fails before cleaning up the database.
        Normally, the built-in pytest teardown_function() accounts for this, but it is not used
        for testing commands (see database_teardown()).
    """

    # Declare communicators outside try block so they are in-scope for the finally block
    ob_communicator = None
    ob_private_communicator = None
    obtmf_private_communicator = None

    try:
        await database_setup()

        ob_user = await sync_get(OBUser, username="ob")
        obtmf_user = await sync_get(OBUser, username="obtmf")
        anon_user = await sync_get(OBUser, username=f"{ANON_PREFIX}0")
        obchat_room = await sync_get(Room, group_type=GroupTypes.Room, name="obchat")
        ob_communicator = await communicator_setup(ob_user, GroupTypes.Room, obchat_room.name)

        ###########################################################################################
        # Test who()                                                                              #
        ###########################################################################################

        # Test invalid room
        await handle_command("/who knobchat", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        correct_response = "knobchat doesn't exist, so that probably means nobody is in there."
        assert json.loads(data_frame)["text"] == correct_response

        # Test empty room
        await handle_command("/w obtmfchat", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        correct_response = "obtmfchat is all empty!"
        assert json.loads(data_frame)["text"] == correct_response

        # Test no arguments
        await handle_command("/w", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        correct_response = "\n".join([
            "Users in obchat:",
            f"    {ob_user} [owner] [you]",
            f"    {obtmf_user} [admin]",
            f"    {anon_user}\n"
        ])
        assert json.loads(data_frame)["text"] == correct_response

        # Test occupied room
        await handle_command("/w obchat", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        assert json.loads(data_frame)["text"] == correct_response

        # Test duplicate room arguments
        await handle_command("/w obchat obchat obchat", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        assert json.loads(data_frame)["text"] == correct_response

        # Test current occupied room, empty room, and invalid room
        await handle_command("/w obchat obtmfchat flobchat", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        correct_response = (
            f"{correct_response}\n"
            "obtmfchat is all empty!\n"
            "flobchat doesn't exist, so that probably means nobody is in there."
        )
        await database_sync_to_async(authenticate)(username="ob", password="ob")
        assert json.loads(data_frame)["text"] == correct_response

        ###########################################################################################
        # Test private()                                                                          #
        ###########################################################################################

        # Test no arguments
        await handle_command("/private", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        correct_response = "Usage: /private /<user> <message>"
        assert json.loads(data_frame)["text"] == correct_response

        # Test syntax error
        await handle_command("/p obtmjeff", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        correct_response = "Looks like you forgot a \"/\" before the username. I'll let it slide."
        assert json.loads(data_frame)["text"] == correct_response

        # Test invalid recipient
        await handle_command("/p /obtmjeff", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        correct_response = ("obtmjeff doesn't exist. Your private message will broadcasted into "
                            "space instead.")
        assert json.loads(data_frame)["text"] == correct_response

        # Test empty message
        await handle_command("/p /obtmf ", ob_user, obchat_room)
        data_frame = await ob_communicator.receive_from()
        correct_response = ("No message specified. Did you give up at just the username?")
        assert json.loads(data_frame)["text"] == correct_response

        # Test private room auto-creation
        await handle_command("/p /ob What's it like to own OBChat?", obtmf_user, obchat_room)

        ob_obtmf_private_room = await sync_get(
            Room,
            group_type=GroupTypes.Private,
            name=get_group_name(GroupTypes.Private, ob_user.id, obtmf_user.id)
        )

        # Test private messaging
        ob_private_communicator = await communicator_setup(
            ob_user,
            GroupTypes.Private,
            obtmf_user.username
        )
        obtmf_private_communicator = await communicator_setup(
            obtmf_user,
            GroupTypes.Private,
            ob_user.username
        )

        await handle_command("/p /obtmf It's pretty cool.", ob_user, obchat_room)
        data_frame = await ob_private_communicator.receive_from()
        second_data_frame = await obtmf_private_communicator.receive_from()
        correct_response = ("It's pretty cool.")
        assert json.loads(data_frame)["text"] == correct_response
        assert json.loads(second_data_frame)["text"] == correct_response

        ###########################################################################################
        # Test create_room()                                                                      #
        ###########################################################################################

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

    finally:
        if ob_communicator:
            await communicator_teardown(ob_communicator)
        if ob_private_communicator:
            await communicator_teardown(ob_private_communicator)
        if obtmf_private_communicator:
            await communicator_teardown(obtmf_private_communicator)

        await database_teardown()

@mark.asyncio
@mark.django_db()
async def test_admin_level():
    """
    Description:
        Tests admin-level commands (see OB.commands.admin_level).
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

        # Test kick() success
        # TODO: kick() test does not remove occupants because that code lies in OBConsumer, which
        # does not exists while testing. Find a way to test this works
        # for occupant in await sync_model_list(obchat_room.occupants):
        #     assert occupant != obtmf_user
        #     assert occupant != mafdtfafobtmf_user
        #     assert occupant != anon_user

        # TODO: Add ban() tests

    finally:
        await database_teardown()
