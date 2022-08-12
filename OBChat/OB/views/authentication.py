"""
Handles HTTP requests depending on the URL the request originated from (see urls.py)
Contains only the authentication views.

See the Django documentation on view functions for more information.
https://docs.djangoproject.com/en/3.0/topics/http/views/
"""

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from OB.models import OBUser


def sign_up(request):
    """
    Handles HTTP requests for the sign-up page.
    GETs the HTML template for the page.
    POSTs the user input in the form and returns errors or saves a new OBUser and redirects to
    the login page.

    Arguments:
        request (AsgiRequest)

    Return values:
        HTML Template: If GET or if POST and the form had errors.
        HTTP Response: If POST and no errors, an HTTP response redirecting to the login page.
    """

    if request.method == "GET":
        template = "OB/sign_up.html"
        return render(request, template)

    if request.method == "POST":
        # Organize form data
        username = request.POST["username"].strip()
        email = request.POST["email"].strip()
        password = request.POST["password"]
        display_name = request.POST["display_name"].strip()
        real_name = request.POST["real_name"].strip().split()
        birthday = request.POST["birthday"] or None

        context = {}

        # Check for errors
        if not all([username, email, password]):
            context["error_message"] = "Please fill out all required fields."
        elif " " in username:
            context["error_message"] = "Username may not contain spaces."
        elif " " in display_name:
            context["error_message"] = "Display name may not contain spaces."
        elif OBUser.objects.filter(username=username.lower()).exists():
            context["error_message"] = "Username already in use."
        elif OBUser.objects.filter(email=email).exists():
            context["error_message"] = "Email already in use."

        first_name = "" if not real_name else real_name[0]
        last_name = "" if len(real_name) <= 1 else " ".join(real_name[1:])

        # Return whichever info was valid to be put back in the form
        if "error_message" in context:
            template = "OB/sign_up.html"
            context.update(
                {
                    "username": username,
                    "email": email,
                    "display_name": display_name or None,
                    "first_name": first_name,
                    "last_name": last_name,
                    "birthday": birthday,
                }
            )
            return render(request, template, context)

        # If no display_name is entered and the username was not all lowercase, make the
        # case-sensitive version of the username the display_name
        if not display_name and not username.islower():
            display_name = username

        # Save a new OBUser to the database
        OBUser.objects.create_user(
            username=username.lower(),
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            birthday=birthday,
        ).save()

        return HttpResponseRedirect(reverse("OB:OB-log_in"))

    # Not GET or POST
    return HttpResponse()


def log_in(request):
    """
    Handles HTTP requests for the login page.
    GETs the HTML template for the page.
    POSTs the user input in the form and returns errors or authenticates the user and redirects to
    the chat list page.

    Arguments:
        request (AsgiRequest)

    Return values:
        HTML Template: If GET or if POST and the form had errors.
        HTTP Response: If POST and no errors, an HTTP response redirecting to the login page.
    """

    template = "OB/log_in.html"

    if request.method == "GET":
        return render(request, template)

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # Log out the user if they are already authenticated
        if request.user.is_authenticated:
            logout(request)

        # Try to authenticate with the data given
        auth_user = authenticate(username=username.lower(), password=password)

        if auth_user is None:
            context = {
                "username": username,
                "error_message": "Invalid username or password.",
            }
            return render(request, template, context)

        login(request, auth_user)

        return HttpResponseRedirect(reverse("OB:OB-chat"))

    # Not GET or POST
    return HttpResponse()


def log_out(request):
    """
    Handles HTTP requests for the logout page.
    Logs the user out.

    Arguments:
        request (AsgiRequest)

    Return values:
        HTTP Response: An HTTP response redirecting to the login page.
    """

    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse("OB:OB-log_in"))
