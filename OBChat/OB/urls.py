from django.urls import path
from . import views

app_name = "OB"
urlpatterns = [
    path("sign_up", views.sign_up, name="OB-sign_up"),
    path("log_in/", views.log_in, name="OB-log_in"),
    path("chat/", views.chat, name="OB-chat")
]
