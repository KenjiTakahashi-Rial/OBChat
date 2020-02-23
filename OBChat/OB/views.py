from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from .models import OBUser


def sign_up(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        display_name = request.POST["display_name"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        if not all([username, email, password, display_name]):
            template = "OB/sign_up.html"
            context = {
                "error_message": "Please fill out all required fields",
                "username": username,
                "email": email,
                "display_name": display_name,
                "first_name": first_name,
                "last_name": last_name
            }
            return render(request, template, context)

        user = User.objects.create_user(username, email, password,
            first_name=first_name, last_name=last_name)
        ob_user = OBUser(user=user, display_name=display_name)
        ob_user.save()

        return HttpResponseRedirect("OB:OB-log_in")

    else:
        template = "OB/sign_up.html"
        return render(request, template)

def log_in(request):
    return None

def chat(request):
    return HttpResponse("OB Chat")

def get_username(request, user_id):
    ob_user = get_object_or_404(OBUser, id=user_id)
    result = f"User {user_id} is named {ob_user.user.username}"

    template = "OB/get_username.html"
    context = { "result": result }
    return render(request, template, context)

