"""
Handles HTTP requests depending on the URL the request originated from (see urls.py)

See the Django documentation on view functions for more information.
https://docs.djangoproject.com/en/3.0/topics/http/views/
"""
# TODO: Organize this into a directory with the functions of similar purpose in different files

import json
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import OBUser, Room, Message
from .utilities import try_get

###################################################################################################
# Authentication                                                                                  #
###################################################################################################

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
        new_user_object = OBUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            birthday=birthday
        )
        new_user_object.save()

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

        # Try to authenticate with the data given
        auth_user = authenticate(username=username, password=password)

        if auth_user is None:
            context = {
                "username": username, 
                "error_message": "Invalid username or password."
            }
            return render(request, template, context)

        login(request, auth_user)

        return HttpResponseRedirect(reverse("OB:OB-chat"))

    return HttpResponse()

###################################################################################################
# Chat Rooms                                                                                      #
###################################################################################################

def chat(request):
    """
    Description:
        Handles HTTP requests for the chat list page.
        GETs the HTML template for the page.

    Arguments:
        request (AsgiRequest)

    Return values:
        The HTML template for the chat list.
    """

    if request.method == "GET":
        template = "OB/chat.html"
        context = {"rooms": Room.objects.all()}
        return render(request, template, context)

    return HttpResponse()

def create_room(request):
    """
    Description:
        Handles HTTP requests for the room creation page.
        GETs the HTML template for the page.
        POSTs the user input in the form and returns errors or saves a new Room and redirects 
        to the new room's page.

    Arguments:
        request (AsgiRequest)

    Return values:
        The HTML template if GET or if POST and the form had errors.
        An HTTP response redirecting to the new room's page if POST and no errors.
    """

    if request.method == "GET":
        if request.user.is_authenticated:
            template = "OB/create_room.html"
            context = {}
        else:
            template = "OB/log_in.html"
            context = {"error_message": "Must be logged in to create a room."}

        return render(request, template, context)

    if request.method == "POST":
        room_name = request.POST["room_name"].strip()
        owner = OBUser.objects.get(username=request.user.username)

        template = "OB/create_room.html"
        context = {"room_name": room_name}

        if not room_name:
            context["error_message"] = "Room must have a name."
            return render(request, template, context)

        if Room.objects.filter(name=room_name).exists():
            context["error_message"] = "Room name already in use."
            return render(request, template, context)

        Room(name=room_name, owner=owner).save()

        return HttpResponseRedirect(reverse("OB:OB-room", kwargs={"room_name": room_name}))

    return HttpResponse()

def room(request, room_name):
    """
    Description:
        Handles HTTP requests for the chat room page.
        GETs the HTML template for the page or an error page if it doesn't exist.

    Arguments:
        request (AsgiRequest)
        room_name (string): The name of the room which may or may not exist.

    Return values:
        The HTML template for the room if GET.
        An error page if GET and the room does not exist.
    """

    if request.method == "GET":
        context = {"room_name": room_name}

        room_object = try_get(Room, name=room_name)

        if room_object:
            messages = Message.objects.filter(room=room_object)

            template = "OB/room.html"
            context["room_name_json"] = mark_safe(json.dumps(room_name))
            context["messages"] = messages
        else:
            template = "OB/not_room.html"

        return render(request, template, context)

    return HttpResponse()

###################################################################################################
# User                                                                                            #
###################################################################################################

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
            context = {"ob_user": user_object}
        else:
            template = "OB/not_user.html"
            context = {}

        return render(request, template, context)

    if request.method == "POST":
        # TODO: Save changed user data
        return None

    return HttpResponse()
