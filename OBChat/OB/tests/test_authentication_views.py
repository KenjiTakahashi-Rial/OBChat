"""
Tests the authentication view functions (see OB.views.authentication).

See the Django documentation on Testing for more information.
https://docs.djangoproject.com/en/3.0/topics/testing/

Also see the pytest documentation for more information.
https://docs.pytest.org/en/latest/contents.html
"""

from pytest import mark

from django.test import Client
from django.urls import reverse

from OB.models import OBUser

def database_setup():
    """
    Description:
        Sets up the database objects required to test the views.

    Arguments:
        None.

    Return values:
        None.
    """

    OBUser.objects.create_user(
        username="ob",
        email="ob@ob.ob",
        password="ob",
        first_name="Kenji",
        last_name="Takahashi-Rial"
    ).save()

@mark.django_db()
def test_sign_up():
    """
    Description:
        Tests the sign up page (see OB.views.authentication.sign_up()).

    Arguments:
        None.

    Return values:
        None.
    """

    client = Client()
    database_setup()

    # Test GET
    response = client.get(reverse("OB:OB-sign_up"))

    assert response.status_code == 200
    assert "error_message" not in response.context

    # Test POST with empty form data
    sign_up_data = {
        "username": "",
        "email": "",
        "password": "",
        "display_name": "",
        "first_name": "",
        "last_name": "",
        "birthday": ""
    }

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Please fill out all required fields."

    # Test POST with invalid username
    sign_up_data["username"] = "O B"
    sign_up_data["email"] = "ob@ob.ob"
    sign_up_data["password"] = "ob"
    sign_up_data["first_name"] = "Kenji"
    sign_up_data["last_name"] = "Takahashi-Rial"

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Username may not contain spaces"

    # Test POST with in-use username
    sign_up_data["username"] = "OB"
    sign_up_data["password"] = "ob"

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Username already in use."

    # Test POST with in-use email
    sign_up_data["username"] = "OBTMF"
    sign_up_data["password"] = "ob"

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Email already in use."

    # Test POST with valid form data
    sign_up_data["username"] = "OBTMF"
    sign_up_data["email"] = "obtmf@ob.ob"
    sign_up_data["password"] = "ob"

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 302

    # Test display_name saving correctly
    OBUser.objects.get(username="obtmf").display_name == "OBTMF"

@mark.django_db()
def test_log_in():
    """
    Description:
        Tests the login page (see OB.views.authentication.log_in()).

    Arguments:
        None.

    Return values:
        None.
    """

    client = Client()
    database_setup()

    # Test GET
    response = client.get(reverse("OB:OB-log_in"))

    assert response.status_code == 200

    # Test POST with empty form data
    log_in_data = {
        "username": "",
        "password": ""
    }

    response = client.post(reverse("OB:OB-log_in"), log_in_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Invalid username or password."

    # Test POST with invalid password
    log_in_data["username"] = "OB"
    log_in_data["password"] = "o"

    response = client.post(reverse("OB:OB-log_in"), log_in_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Invalid username or password."

    # Test POST with valid form data
    log_in_data["username"] = "OB"
    log_in_data["password"] = "ob"

    response = client.post(reverse("OB:OB-log_in"), log_in_data)
    assert response.status_code == 302
