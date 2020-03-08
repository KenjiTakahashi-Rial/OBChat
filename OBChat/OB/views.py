import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
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

        template = "OB/sign_up.html"
        context = {
            "username": username,
            "email": email,
            "display_name": display_name,
            "first_name": first_name,
            "last_name": last_name
        }   

        if not all([username, email, password, display_name]):
            context["error_message"] = "Please fill out all required fields."
            return render(request, template, context)

        if " " in username:
            context["error_message"] = "Username may not contain spaces"
            return render(request, template, context)

        if User.objects.filter(username=username).exists():
            context["error_message"] = "Username already in use."
            return render(request, template, context)

        if User.objects.filter(email=email).exists():
            context["error_message"] = "Email already in use."
            return render(request, template, context)

        user = User.objects.create_user(username, email, password,
                                        first_name=first_name,
                                        last_name=last_name)
        
        OBUser(user=user, display_name=display_name).save()

        return HttpResponseRedirect(reverse("OB:OB-log_in"))


def log_in(request):
    if request.method == "GET":
        template = "OB/log_in.html"
        return render(request, template)

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)

        if user is None:
            context = {"error_message": "Invalid username or password."}
            return render(request, template, context)

        login(request, user)

        return HttpResponseRedirect(reverse("OB:OB-chat"))

def chat(request):
    if request.method == "GET":
        template = "OB/chat.html"
        context = {"rooms": Room.objects.all()}
        return render(request, template, context)

def create_room(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            template = "OB/create_room.html"
            context =  {}
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
            context["error_message"] = "Room must have a name.",
            return render(request, template, context)

        if Room.objects.filter(name=room_name).exists():
            context["error_message"] = "Room name already in use."
            return render(request, template, context)

        Room(name=room_name, owner=owner).save()

        return HttpResponseRedirect(reverse("OB:OB-room", kwargs={"room_name": room_name}))

def room(request, room_name):
    if request.method == "GET":
        context = {"room_name": room_name}

        if Room.objects.filter(name=room_name).exists():
            template = "OB/room.html"
            context["room_name_json"] = mark_safe(json.dumps(room_name))
        else:
            template = "OB/not_room.html"

        return render(request, template, context)

    # Handles commands and saves the message
    # The message is actually sent in consumers.py
    if request.method == "POST":
        message = request.POST["message"].strip()
        
        if not message:
            return

        if message[0] == '/':
            if len(message) == 1 or message[1] != '/':
                command(request, message)
