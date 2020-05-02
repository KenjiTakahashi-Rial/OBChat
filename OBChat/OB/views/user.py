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

    context = {"user": try_get(OBUser, username=username)}

    if request.method == "GET":
        if context["user"]:
            template = "OB/user.html"
        else:
            template = "OB/not_user.html"

        return render(request, template, context)

    if request.method == "POST":
        # Ensure that only the user whose page this is can edit their information
        if request.user.username != username:
            return HttpResponse()

        # Organize all the data
        display_name = request.POST.get("display-name")
        real_name = request.POST.get("real-name")
        birthday = request.POST.get("birthday")

        template = "OB/user.html"

        # Check for errors
        if " " in display_name:
            context["error_message"] = "Display name may not contain spaces."

        if "error_message" in context:
            return render(request, template, context)

        # Display name
        if not display_name or display_name == request.user.display_name:
            request.user.display_name = None
        else:
            request.user.display_name = display_name.strip()

        # First and last names
        if real_name:
            split_name = real_name.strip().split()

            request.user.first_name = split_name[0]

            if len(split_name) > 1:
                print(split_name)
                request.user.last_name = " ".join(split_name[1:])
            else:
                request.user.last_name = ""

        # Birthday
        if birthday and birthday != request.user.birthday:
            request.user.birthday = birthday

        request.user.save()

        return render(request, template)

    # Not GET or POST
    return HttpResponse()
