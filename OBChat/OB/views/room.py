"""
Handles HTTP requests depending on the URL the request originated from (see urls.py)
Contains only the room views.

See the Django documentation on view functions for more information.
https://docs.djangoproject.com/en/3.0/topics/http/views/
"""

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from OB.models import OBUser, Room, Message
from OB.utilities.database import try_get
from OB.utilities.format import get_datetime_string

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

        # Check for errors
        if not room_name:
            context["error_message"] = "Room must have a name."
            return render(request, template, context)

        if Room.objects.filter(name=room_name.lower()).exists():
            context["error_message"] = "Room name already in use."
            return render(request, template, context)

        # Save the room
        Room(
            name=room_name.lower(),
            display_name=room_name,
            owner=owner
        ).save()

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
        room_object = try_get(Room, name=room_name)

        if room_object:
            # Get the messages
            room_name_json = mark_safe(json.dumps(room_name))
            message_objects = Message.objects.filter(room=room_object)
            messages_timestrings = [(message, get_datetime_string(message.timestamp))\
                                    for message in message_objects]

            template = "OB/room.html"
            context = {
                "room_name": room_object.display_name,
                "room_name_json": room_name_json,
                "messages": messages_timestrings
            }
        else:
            # Return the room does not exist page
            template = "OB/not_room.html"
            context = {"room_name": room_name}

        return render(request, template, context)

    return HttpResponse()
