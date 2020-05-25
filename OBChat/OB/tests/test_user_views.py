"""
Tests the user view functions (see OB.views.user).

See the Django documentation on Testing for more information.
https://docs.djangoproject.com/en/3.0/topics/testing/

Also see the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from datetime import date

from pytest import mark

from django.test import Client
from django.urls import reverse

from OB.constants import GroupTypes
from OB.models import OBUser, Room
from OB.utilities.format import get_group_name

def setup_function():
    """
    Description:
        Sets up the database objects required to test the views.

        This is a built-in pytest fixture that runs before every function.
        See the pytest documentation on xunit-style setup for more information.
        https://docs.pytest.org/en/latest/xunit_setup.html
    """

    OBUser.objects.create_user(
        username="ob",
        email="ob@ob.ob",
        password="ob"
    ).save()

    OBUser.objects.create_user(
        username="obtmf",
        email="obtmf@ob.ob",
        password="ob"
    ).save()

def teardown_function():
    """
    Description:
        Cleans up the database objects used to test the views.

        This is a built-in pytest fixture that runs after every function.
        See the pytest documentation on xunit-style setup for more information.
        https://docs.pytest.org/en/latest/xunit_setup.html
    """

    for user in OBUser.objects.all():
        user.delete()

@mark.django_db()
def test_user():
    """
    Description:
        Tests the user information page (see OB.views.user.user()).
    """

    client = Client()

    # Test invalid username GET
    response = client.get(reverse("OB:OB-user", kwargs={"username": "mafdtfafobtmf"}))

    assert response.status_code == 200

    # Test anonymous GET
    response = client.get(reverse("OB:OB-user", kwargs={"username": "ob"}))

    assert response.status_code == 200

    # Test other user authenticated GET
    client.login(username="obtmf", password="ob")

    response = client.get(reverse("OB:OB-user", kwargs={"username": "ob"}))

    assert response.status_code == 200

    # Test user's own page GET
    client.logout()
    client.login(username="ob", password="ob")

    response = client.get(reverse("OB:OB-user", kwargs={"username": "ob"}))

    assert response.status_code == 200

    # Test anonymous POST (this should not be possible)
    client.logout()

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}))

    assert response.status_code == 200

    # Test other user authenticated POST (this should not be possible)
    client.login(username="obtmf", password="ob")

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}))

    assert response.status_code == 200

    # Test user's own page POST with empty form data (this should not be possible)
    client.logout()
    client.login(username="ob", password="ob")

    user_edit_data = {
        "display-name": "",
        "real-name": "",
        "birthday": ""
    }

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200

    # Test POST with invalid display name
    user_edit_data["display-name"] = "O B"

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Display name may not contain spaces."

    # Test POST with display name only
    user_edit_data["display-name"] = "OBT"

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200
    assert OBUser.objects.get(username="ob").display_name == "OBT"

    # Test POST with different display name only
    user_edit_data["display-name"] = "OBTMF"

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200
    assert OBUser.objects.get(username="ob").display_name == "OBTMF"

    # Test POST with first name only
    user_edit_data["real-name"] = "Kenji"

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200
    ob_user = OBUser.objects.get(username="ob")
    assert ob_user.first_name == "Kenji"
    assert not ob_user.last_name

    # Test POST with first and last name
    user_edit_data["real-name"] = "Kenji TR"

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200
    ob_user = OBUser.objects.get(username="ob")
    assert ob_user.first_name == "Kenji"
    assert ob_user.last_name == "TR"

    # Test POST with different first and last name
    user_edit_data["real-name"] = "Kenji Takahashi-Rial-La"

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200
    ob_user = OBUser.objects.get(username="ob")
    assert ob_user.first_name == "Kenji"
    assert ob_user.last_name == "Takahashi-Rial-La"

    # Test POST with birthday only
    user_edit_data["birthday"] = "2020-05-01"

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200
    assert OBUser.objects.get(username="ob").birthday == date(2020, 5, 1)

    # Test POST with different birthday
    user_edit_data["birthday"] = "1987-10-14"

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200
    assert OBUser.objects.get(username="ob").birthday == date(1987, 10, 14)

    # Test POST with all data
    user_edit_data["display-name"] = "OB"
    user_edit_data["real-name"] = "Kenji Takahashi-Rial"
    user_edit_data["birthday"] = "1997-10-14"

    response = client.post(reverse("OB:OB-user", kwargs={"username": "ob"}), user_edit_data)

    assert response.status_code == 200
    ob_user = OBUser.objects.get(username="ob")
    assert ob_user.display_name == "OB"
    assert ob_user.first_name == "Kenji"
    assert ob_user.last_name == "Takahashi-Rial"
    assert ob_user.birthday == date(1997, 10, 14)

@mark.django_db()
def test_private():
    """
    Description:
        Tests the private message page (see OB.views.user.private()).
    """

    client = Client()

    # Test anonymous GET
    response = client.get(reverse("OB:OB-private", kwargs={"username": "ob"}))

    assert response.status_code == 200
    assert response.context["error_message"] == "Must be logged in to send private messages."

    # Test invalid user GET
    client.login(username="ob", password="ob")
    response = client.get(reverse("OB:OB-private", kwargs={"username": "mafdtfafobtmf"}))

    assert response.status_code == 200
    assert "error_message" not in response.context

    # Test valid user GET
    response = client.get(reverse("OB:OB-private", kwargs={"username": "obtmf"}))

    assert response.status_code == 200
    ob_id = OBUser.objects.get(username="ob").id
    obtmf_id = OBUser.objects.get(username="obtmf").id
    assert response.context["room_name"] == get_group_name(GroupTypes.Private, ob_id, obtmf_id)
    assert "messages" in response.context and "websocket_url_json" in response.context

    # Test private message Room created
    Room.objects.get(group_type=GroupTypes.Private)
