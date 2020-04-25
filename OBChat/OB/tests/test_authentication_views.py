"""
Tests the authentication view functions (see OB.views.authentication).

See the Django documentation on Testing for more information.
https://docs.djangoproject.com/en/3.0/topics/testing/
"""

from django.test import Client
from django.test import TestCase
from django.urls import reverse

from OB.models import OBUser

class TestAuthenticationViews(TestCase):
    def setUp(self):
        """
        Description:
            Setup phase before every test method. Unfortunately this is overriden from a Django
            TestCase method, so it must be camelCase instead of snake_case like everything else.
            Sets up an OBUser database object to test the views.

        Arguments:
            self (TestCase): A Django TestCase class.

        Return values:
            None
        """

        self.client = Client()

        OBUser.objects.create_user(
            username="OB",
            email="ob@ob.ob",
            password="ob",
            first_name="Kenji",
            last_name="Takahashi-Rial"
        ).save()

    def test_sign_up(self):
        """
        Description:
            Test signing up with and without form errors (see OB.views.authentication.sign_up()).

        Arguments:
            self (TestCase): A Django TestCase class.

        Return values:
            None
        """

        # Test GET
        response = self.client.get(reverse("OB:OB-sign_up"))

        self.assertEqual(response.status_code, 200)

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

        response = self.client.post(reverse("OB:OB-sign_up"), sign_up_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error_message"], "Please fill out all required fields.")

        # Test POST with invalid username
        sign_up_data["username"] = "O B"
        sign_up_data["email"] = "ob@ob.ob"
        sign_up_data["password"] = "ob"
        sign_up_data["first_name"] = "Kenji"
        sign_up_data["last_name"] = "Takahashi-Rial"

        response = self.client.post(reverse("OB:OB-sign_up"), sign_up_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error_message"], "Username may not contain spaces")

        # Test POST with in-use username
        sign_up_data["username"] = "OB"
        sign_up_data["password"] = "ob"

        response = self.client.post(reverse("OB:OB-sign_up"), sign_up_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error_message"], "Username already in use.")

        # Test POST with in-use email
        sign_up_data["username"] = "OBTMF"
        sign_up_data["password"] = "ob"

        response = self.client.post(reverse("OB:OB-sign_up"), sign_up_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error_message"], "Email already in use.")

        # Test POST with valid form data
        sign_up_data["username"] = "OBTMF"
        sign_up_data["email"] = "obtmf@ob.ob"
        sign_up_data["password"] = "ob"

        response = self.client.post(reverse("OB:OB-sign_up"), sign_up_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse("error_message" in response.context)

    def test_log_in(self):
        """
        Description:
            Test logging in with and without form errors(see OB.views.authentication.sign_up()).

        Arguments:
            self (TestCase): A Django TestCase class.

        Return values:
            None
        """

        # Test GET
        response = self.client.get(reverse("OB:OB-log_in"))

        self.assertEqual(response.status_code, 200)

        # Test POST with empty form data
        log_in_data = {
            "username": "",
            "password": ""
        }

        response = self.client.post(reverse("OB:OB-log_in"), log_in_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error_message"], "Invalid username or password.")

        # Test POST with invalid password
        log_in_data["username"] = "OB"
        log_in_data["password"] = "o"

        response = self.client.post(reverse("OB:OB-log_in"), log_in_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error_message"], "Invalid username or password.")

        # Test POST with valid form data
        log_in_data["username"] = "OB"
        log_in_data["password"] = "ob"

        response = self.client.post(reverse("OB:OB-log_in"), log_in_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse("error_message" in response.context)
