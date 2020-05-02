"""
Tests the room view functions (see OB.views.room).

See the Django documentation on Testing for more information.
https://docs.djangoproject.com/en/3.0/topics/testing/

Also see the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

# TODO: Check after each successful POST that all OBUser attributes are correct

from pytest import mark

from django.test import Client
from django.urls import reverse

from OB.models import OBUser, Room

def database_setup():
    """
    Description:
        Sets up the database objects required to test the views.

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

def database_cleanup():
    """
    Description:
        Cleans up the database objects used to test the views.

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
    database_setup()

    # Test GET
    response = client.get(reverse("OB:OB-chat"))

    assert response.status_code == 200
    assert "error_message" not in response.context

    database_cleanup()

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
    database_setup()

    # Test GET with unauthenticated user
    response = client.get(reverse("OB:OB-create_room"))

    assert response.status_code == 200
    assert response.context["error_message"] == "Must be logged in to create a room."

    # Authenticate user and test GET
    client.login(username="ob", password="ob")

    response = client.get(reverse("OB:OB-create_room"))

    assert response.status_code == 200
    assert "error_message" not in response.context

    # Test POST with empty form data
    create_room_data = {"room_name": ""}

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

    # Test POST with valid form data
    create_room_data["room_name"] = "knobchat"

    response = client.post(reverse("OB:OB-create_room"), create_room_data)

    assert response.status_code == 302
    assert not response.context

    # Test room saving correctly
    Room.objects.get(name="knobchat")

    database_cleanup()

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
    database_setup()

    # Test GET with invalid room name
    response = client.get(reverse("OB:OB-room", kwargs={"room_name": "knobchat"}))

    assert response.status_code == 200
    assert response.context["room_name"] == "knobchat"

    # Test GET with valid room name
    response = client.get(reverse("OB:OB-room", kwargs={"room_name": "obchat"}))

    assert response.status_code == 200
    assert "messages" in response.context

    database_cleanup()
