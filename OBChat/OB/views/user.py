"""
Handles HTTP requests depending on the URL the request originated from (see urls.py)
Contains only the user views.

See the Django documentation on view functions for more information.
https://docs.djangoproject.com/en/3.0/topics/http/views/
"""

from django.http import HttpResponse
from django.shortcuts import render

from OB.models import OBUser
from OB.utilities.database import try_get

def user(request, username):
    """
    Description:
        Handles HTTP requests for the user info page
        GETs the HTML template for the page or an error page if it doesn't exist
        POSTs the user input in the form and returns errors or saves the OBUser

    Arguments:
        request (AsgiRequest)
        username (string): The name of the user which may or may not exist.

    Return values:
        The HTML template for the room if GET or if POST and the form had errors.
        An error page if GET and the user does not exist.
        An empty HTTP response if POST and no errors.
    """

    if request.method == "GET":
        user_object = try_get(OBUser, username=username)

        if user_object:
            template = "OB/user.html"
            context = {"user": user_object}
        else:
            template = "OB/not_user.html"
            context = {}

        return render(request, template, context)

    if request.method == "POST":
        # TODO: Save changed user data
        return None

    return HttpResponse()
