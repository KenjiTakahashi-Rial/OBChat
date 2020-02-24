from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.urls import reverse
from .models import OBUser


def sign_up(request):
    if request.method != "POST":
        template = "OB/sign_up.html"
        return render(request, template)

    else:
        username = request.POST["username"].strip()
        email = request.POST["email"].strip()
        password = request.POST["password"]
        display_name = request.POST["display_name"].strip()
        first_name = request.POST["first_name"].strip()
        last_name = request.POST["last_name"].strip()

        template = "OB/sign_up.html"
        context = {
            "error_message": "Please fill out all required fields.",
            "username": username,
            "email": email,
            "display_name": display_name,
            "first_name": first_name,
            "last_name": last_name
        }

        if not all([username, email, password, display_name]):
            return render(request, template, context)

        if User.objects.get(email=email).exists():
            context["error_message"] = "Email already in use."
            return render(request, template, context)

        try:
            user = User.objects.create_user(username, email, password,
                                            first_name=first_name,
                                            last_name=last_name)
            ob_user = OBUser(user=user, display_name=display_name)
            ob_user.save()
        except IntegrityError:
            context["error_message"] = "Username already in use."
            return render(request, template, context)

        return HttpResponseRedirect(reverse("OB:OB-log_in"))


def log_in(request):
    template = "OB/log_in.html"

    if request.method != "POST":
        return render(request, template)

    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("OB:OB-chat"))
        else:
            context = {"error_message": "Invalid username or password."}
            return render(request, template, context)


def chat(request):
    template = "OB/chat.html"
    return render(request, template)
