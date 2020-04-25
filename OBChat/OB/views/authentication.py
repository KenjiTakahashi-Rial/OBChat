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
    Description:
        Handles HTTP requests for the sign-up page.
        GETs the HTML template for the page.
        POSTs the user input in the form and returns errors or saves a new OBUser and redirects
        to the login page.

    Arguments:
        request (AsgiRequest)

    Return values:
        The HTML template if GET or if POST and the form had errors.
        An HTTP response redirecting to the login page if POST and no errors.
    """

    if request.method == "GET":
        template = "OB/sign_up.html"
        return render(request, template)

    if request.method == "POST":
        # Strip all the form data of leading/trailing whitespace
        username = request.POST["username"].strip()
        email = request.POST["email"].strip()
        password = request.POST["password"]
        display_name = request.POST["display_name"].strip()
        first_name = request.POST["first_name"].strip()
        last_name = request.POST["last_name"].strip()
        birthday = request.POST["birthday"] if request.POST["birthday"] else None

        context = {}

        # Check for errors
        if not all([username, email, password]):
            context["error_message"] = "Please fill out all required fields."
        elif " " in username:
            context["error_message"] = "Username may not contain spaces"
        elif OBUser.objects.filter(username=username).exists():
            context["error_message"] = "Username already in use."
        elif OBUser.objects.filter(email=email).exists():
            context["error_message"] = "Email already in use."

        if "error_message" in context:
            template = "OB/sign_up.html"
            # Return whichever info was valid to be put back in the form
            context.update({
                "username": username,
                "email": email,
                "display_name": display_name,
                "first_name": first_name,
                "last_name": last_name,
                "birthday": birthday
            })
            return render(request, template, context)

        # Save a new OBUser to the database
        OBUser.objects.create_user(
            username=username.lower(),
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name or username,
            birthday=birthday
        ).save()

        return HttpResponseRedirect(reverse("OB:OB-log_in"))

    return HttpResponse()

def log_in(request):
    """
    Description:
        Handles HTTP requests for the login page.
        GETs the HTML template for the page.
        POSTs the user input in the form and returns errors or authenticates the user and redirects
        to the chat list page.

    Arguments:
        request (AsgiRequest)

    Return values:
        The HTML template if GET or if POST and the form had errors.
        An HTTP response redirecting to the chat list page if POST and no errors.
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
                "error_message": "Invalid username or password."
            }
            return render(request, template, context)

        login(request, auth_user)

        return HttpResponseRedirect(reverse("OB:OB-chat"))

    return HttpResponse()

def log_out(request):
    """
    Description:
        Handles HTTP requests for the logout page.
        Logs the user out.

    Arguments:
        request (AsgiRequest)

    Return values:
        An HTTP response redirecting to the login page.
    """

    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse("OB:OB-log_in"))
