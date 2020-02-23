from django.urls import path
from . import views

app_name = "OB"
urlpatterns = [
    path("sign_up", views.sign_up, name="OB-sign_up"),
    path("login/", views.log_in, name="OB-log_in"),
    path("chat/", views.chat, name="OB-chat"),
    path("user/<int:user_id>/", views.get_username, name="OB-get_username")
]