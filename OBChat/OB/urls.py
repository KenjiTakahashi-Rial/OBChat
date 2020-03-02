from django.urls import path
from django.conf.urls import url
from . import views

app_name = "OB"
urlpatterns = [
    path("sign_up", views.sign_up, name="OB-sign_up"),
    path("log_in/", views.log_in, name="OB-log_in"),
    path("chat/", views.chat, name="OB-chat"),
    path("create_room/", views.create_room, name="OB-create_room"),
    url(r"^chat/(?P<room_name>[-\w]+)/$", views.room, name="OB-room")
]
