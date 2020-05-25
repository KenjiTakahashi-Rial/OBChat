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
        password="ob",
        first_name="Kenji",
        last_name="Takahashi-Rial"
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
def test_sign_up():
    """
    Description:
        Tests the sign up page (see OB.views.authentication.sign_up()).
    """

    client = Client()

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
        "real_name": "",
        "birthday": ""
    }

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Please fill out all required fields."

    # Test POST with invalid username
    sign_up_data["username"] = "O B"
    sign_up_data["email"] = "ob@ob.ob"
    sign_up_data["password"] = "ob"
    sign_up_data["real_name"] = "Kenji"

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Username may not contain spaces."


    # Test POST with in-use username
    sign_up_data["username"] = "OB"

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Username already in use."

    # Test POST with in-use email
    sign_up_data["username"] = "OBTMF"

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 200
    assert response.context["error_message"] == "Email already in use."

    # Test POST with valid form data, first name only
    sign_up_data["username"] = "OBTMF"
    sign_up_data["email"] = "obtmf@ob.ob"

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert response.status_code == 302
    assert not response.context

    # Test user saving correctly
    assert OBUser.objects.get(email="obtmf@ob.ob").username == "obtmf"
    assert OBUser.objects.get(username="obtmf").display_name == "OBTMF"

    # Test POST with valid form data, first and last name
    sign_up_data["username"] = "MAFDTFAFOBTMF"
    sign_up_data["email"] = "mafdtfafobtmf@ob.ob"
    sign_up_data["real_name"] = "Kenji Takahashi-Rial"

    response = client.post(reverse("OB:OB-sign_up"), sign_up_data)

    assert OBUser.objects.get(username="mafdtfafobtmf").first_name == "Kenji"
    assert OBUser.objects.get(username="mafdtfafobtmf").last_name == "Takahashi-Rial"

@mark.django_db()
def test_log_in():
    """
    Description:
        Tests the login page (see OB.views.authentication.log_in()).
    """

    client = Client()

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
    assert not response.context
