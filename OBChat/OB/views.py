import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from .commands import command
from .models import OBUser, Room, Message


def sign_up(request):
    if request.method == "GET":
        template = "OB/sign_up.html"
        return render(request, template)

    if request.method == "POST":
        username = request.POST["username"].strip()
        email = request.POST["email"].strip()
        password = request.POST["password"]
        display_name = request.POST["display_name"].strip()
        first_name = request.POST["first_name"].strip()
        last_name = request.POST["last_name"].strip()
        birthday = request.POST["birthday"]

        template = "OB/sign_up.html"
        context = {
            "username": username,
            "email": email,
            "display_name": display_name,
            "first_name": first_name,
            "last_name": last_name,
            "birthday": birthday
        }

        if not all([username, email, password]):
            context["error_message"] = "Please fill out all required fields."
        elif " " in username:
            context["error_message"] = "Username may not contain spaces"
        elif User.objects.filter(username=username).exists():
            context["error_message"] = "Username already in use."
        elif User.objects.filter(email=email).exists():
            context["error_message"] = "Email already in use."

        if "error_message" in context:
            return render(request, template, context)

        user_entry = User.objects.create_user(username, email, password,
                                              first_name=first_name,
                                              last_name=last_name)

        OBUser(user=user_entry, display_name=display_name, birthday=birthday).save()

        return HttpResponseRedirect(reverse("OB:OB-log_in"))

    return None

def log_in(request):
    if request.method == "GET":
        template = "OB/log_in.html"
        return render(request, template)

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user_entry = authenticate(username=username, password=password)

        if user is None:
            context = {"error_message": "Invalid username or password."}
            return render(request, template, context)

        login(request, user_entry)

        return HttpResponseRedirect(reverse("OB:OB-chat"))

    return None

def chat(request):
    if request.method == "GET":
        template = "OB/chat.html"
        context = {"rooms": Room.objects.all()}
        return render(request, template, context)

    return None

def create_room(request):
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
        owner = OBUser.objects.get(user=request.user)

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

    return None

def room(request, room_name):
    if request.method == "GET":
        context = {"room_name": room_name}

        try:
            room_entry = Room.objects.get(name=room_name)
            messages = Message.objects.filter(room=room_entry)

            template = "OB/room.html"
            context["room_name_json"] = mark_safe(json.dumps(room_name))
            context["messages"] = messages if messages.exists() else None
        except (MultipleObjectsReturned, ObjectDoesNotExist) as exception:
            print(exception)
            template = "OB/not_room.html"

        return render(request, template, context)

    # Handles commands and saves the message in the database
    # The message is sent to others in consumers.py
    if request.method == "POST":
        message = request.POST["message"].strip()

        if message:
            if message[0] == '/':
                if len(message) == 1 or message[1] != '/':
                    command(request, room_name, message)
            else:
                try:
                    sender_entry = OBUser.objects.get(user=request.user)
                    room_entry = Room.objects.get(name=room_name)

                    Message(message=message, sender=sender_entry, room=room_entry).save()
                except (MultipleObjectsReturned, ObjectDoesNotExist) as exception:
                    print(exception)

        return HttpResponse()

    return None

def user(request, username):
    if request.method == "GET":
        user_entry = User.objects.filter(username=username)

        if user_entry.exists():
            ob_user_entry = OBUser.objects.get(user=user_entry.first())

            template = "OB/user.html"
            context = {"ob_user": ob_user_entry}
        else:
            template = "OB/not_user.html"
            context = {}

        return render(request, template, context)

    if request.method == "POST":
        return None

    return None
