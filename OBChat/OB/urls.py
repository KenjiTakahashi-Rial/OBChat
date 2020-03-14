from django.conf.urls import url
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = "OB"
urlpatterns = [
    url("favicon.ico", RedirectView.as_view(
        url=staticfiles_storage.url("favicon.ico"), 
        permanent=False), name="favicon"),
    path("sign_up/", views.sign_up, name="OB-sign_up"),
    path("log_in/", views.log_in, name="OB-log_in"),
    path("chat/", views.chat, name="OB-chat"),
    path("", views.chat, name="OB-/"),
    path("create_room/", views.create_room, name="OB-create_room"),
    url(r"^chat/(?P<room_name>[-\w]+)/$", views.room, name="OB-room")
]
