"""
Determines the function in views.py to call when a request is received from a URL

See the Django documentation on the URL dispatcher for more information.
https://docs.djangoproject.com/en/3.0/topics/http/urls/
"""

from django.conf.urls import url
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic.base import RedirectView

from OB.views.authentication import log_in, log_out, sign_up
from OB.views.room import chat, create_room, room
from OB.views.user import private, user

app_name = "OB"
urlpatterns = [
    url(
        "favicon.ico",
        RedirectView.as_view(
            url=staticfiles_storage.url("favicon.ico"),
            permanent=False
        ),
        name="favicon"
    ),

    # Authentication
    path("log_in/", log_in, name="OB-log_in"),
    path("log_out/", log_out, name="OB-log_out"),
    path("sign_up/", sign_up, name="OB-sign_up"),

    # Room
    path("", chat, name="OB-/"),
    path("chat/", chat, name="OB-chat"),
    path("create_room/", create_room, name="OB-create_room"),
    url(r"^chat/(?P<room_name>[-\w]+)/$", room, name="OB-room"),

    # User
    url(r"^private/(?P<username>[-\w]+)/$", private, name="OB-private"),
    url(r"^user/(?P<username>[-\w]+)/$", user, name="OB-user")
]
