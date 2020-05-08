"""
Tests the room view functions (see OB.views.room).

See the Django documentation on Testing for more information.
https://docs.djangoproject.com/en/3.0/topics/testing/

Also see the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from django.test import Client
from django.urls import reverse

from OB.constants import GroupTypes
from OB.models import OBUser, Room

def setup_function():
    """
    Description:
        Sets up the database objects required to test the views.

        This is a built-in pytest fixture that runs before every function.
        See the pytest documentation on xunit-style setup for more information.
        https://docs.pytest.org/en/latest/xunit_setup.html

    Arguments:
        None.

    Return values:
        None.
    """

    ob_user = OBUser.objects.create_user(
        username="ob",
        email="ob@ob.ob",
        password="ob",
        first_name="Kenji",
        last_name="Takahashi-Rial"
    ).save()

    Room(
        name="obchat",
        owner=ob_user
    ).save()

def teardown_function():
    """
    Description:
        Cleans up the database objects used to test the views.

        This is a built-in pytest fixture that runs after every function.
        See the pytest documentation on xunit-style setup for more information.
        https://docs.pytest.org/en/latest/xunit_setup.html

    Arguments:
        None.

    Return values:
        None.
    """

    for user in OBUser.objects.all():
        user.delete()

    for room in Room.objects.all():
        room.delete()

@mark.django_db()
def test_chat():
    """
    Description:
        Tests the chat list page (see OB.views.room.chat()).

    Arguments:
        None.

    Return values:
        None.
    """

    client = Client()

    # Test GET
    response = client.get(reverse("OB:OB-chat"))

    assert response.status_code == 200
    assert "error_message" not in response.context

@mark.django_db()
def test_create_room():
    """
    Description:
        Tests the room creation page (see OB.views.room.create_room()).

    Arguments:
        None.

    Return values:
        None.
    """

    client = Client()

    # Test GET with unauthenticated user
    response = client.get(reverse("OB:OB-create_room"))

    assert response.status_code == 200
    assert response.context["error_message"] == "Must be logged in to create a room."

    # Test GET with authenticated user
    client.login(username="ob", password="ob")

    response = client.get(reverse("OB:OB-create_room"))

    assert response.status_code == 200
    assert "error_message" not in response.context

    # Test POST with empty form data
    create_room_data = {
        "room_name": "",
        "display_name": ""
    }

    response = client.post(reverse("OB:OB-create_room"), create_room_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Room must have a name."

    # Test POST with invalid room name
    create_room_data["room_name"] = "ob chat"

    response = client.post(reverse("OB:OB-create_room"), create_room_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Room name cannot contain spaces."

    # Test POST with in-use room name
    create_room_data["room_name"] = "obchat"

    response = client.post(reverse("OB:OB-create_room"), create_room_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Room name already in use."

    # Test POST with invalid display name
    create_room_data["room_name"] = "knobchat"
    create_room_data["display_name"] = "OB Chat"

    response = client.post(reverse("OB:OB-create_room"), create_room_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Display name cannot contain spaces."

    # Test POST with valid form data, no display name
    create_room_data["display_name"] = ""

    response = client.post(reverse("OB:OB-create_room"), create_room_data)

    assert response.status_code == 302
    assert not response.context

    # Test room saving correctly
    knobchat_room = Room.objects.get(group_type=GroupTypes.Room, name="knobchat")
    assert knobchat_room.owner == OBUser.objects.get(username="ob")

    # Test display name not saving
    assert not knobchat_room.display_name

    # Test POST with valid form data, automatic display name
    create_room_data["room_name"] = "LobChat"

    response = client.post(reverse("OB:OB-create_room"), create_room_data)

    assert response.status_code == 302
    assert not response.context

    # Test display name saving correctly
    assert Room.objects.get(name="lobchat").display_name == "LobChat"

    # Test POST with valid form data, explicit display name
    create_room_data["room_name"] = "JobChat"
    create_room_data["display_name"] = "ChobChat"

    response = client.post(reverse("OB:OB-create_room"), create_room_data)

    assert response.status_code == 302
    assert not response.context

    # Test display name saving correctly
    assert Room.objects.get(name="jobchat").display_name == "ChobChat"

@mark.django_db()
def test_room():
    """
    Description:
        Tests the room page (see OB.views.room.room()).

    Arguments:
        None.

    Return values:
        None.
    """

    client = Client()

    # Test GET with invalid room name
    response = client.get(reverse("OB:OB-room", kwargs={"room_name": "knobchat"}))

    assert response.status_code == 200
    assert response.context["room_name"] == "knobchat"

    # Test GET with valid room name
    response = client.get(reverse("OB:OB-room", kwargs={"room_name": "obchat"}))

    assert response.status_code == 200
    assert "messages" in response.context
