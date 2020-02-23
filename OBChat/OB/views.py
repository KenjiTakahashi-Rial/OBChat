from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import OBUser


def sign_up(request):
    return None

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

