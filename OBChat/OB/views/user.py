"""
Handles HTTP requests depending on the URL the request originated from (see urls.py)
Contains only the user views.

See the Django documentation on view functions for more information.
https://docs.djangoproject.com/en/3.0/topics/http/views/
"""

import json

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from OB.constants import GroupTypes
from OB.models import Message, OBUser, Room
from OB.utilities.database import try_get
from OB.utilities.format import get_datetime_string, get_group_name


def user(request, username):
    """
    Handles HTTP requests for the user info page
    GETs the HTML template for the page or an error page if it doesn't exist
    POSTs the user input in the form and returns errors or saves the OBUser

    Arguments:
        request (AsgiRequest)
        username (string): The name of the user which may or may not exist.

    Return values:
        HTML Template: If GET or if POST and the form had errors, returns the HTML template for
            the room or an error page if the user does not exist.
        HTTP Response: An empty HTTP response if POST and no errors.
    """

    template = "OB/user.html"
    context = {"user": try_get(OBUser, username=username)}

    if request.method == "GET":
        if not context["user"]:
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


def private(request, username):
    """
    Handles HTTP requests for the private message page
    GETs the HTML template for the page or an error page if it doesn't exist

    Arguments:
        request (AsgiRequest)
        username (string): The name of the target user to private message.

    Return values:
        HTML Template: If GET, returns the HTML template for the room or an error page if the room
            does not exist.
    """

    if request.method == "GET":
        template = "OB/room.html"
        context = {}

        target_user = try_get(OBUser, username=username)

        if not request.user.is_authenticated:
            template = "OB/log_in.html"
            context = {"error_message": "Must be logged in to send private messages."}
        elif not target_user:
            template = "OB/not_user.html"
        else:
            private_room_name = get_group_name(
                GroupTypes.Private, request.user.id, target_user.id
            )
            room = try_get(Room, group_type=GroupTypes.Private, name=private_room_name)

            if not room:
                room = Room(
                    group_type=GroupTypes.Private, name=private_room_name
                ).save()

            # Get the messages
            websocket_url_json = mark_safe(
                json.dumps(f"ws://{{0}}/OB/private/{username}/")
            )
            messages = Message.objects.filter(room=room)
            messages_timestrings = [
                (message, get_datetime_string(message.timestamp))
                for message in messages
            ]

            template = "OB/room.html"
            context = {
                "room_name": room.name,
                "websocket_url_json": websocket_url_json,
                "messages": messages_timestrings,
            }

        return render(request, template, context)

    return HttpResponse()
