from django.urls import path
from . import views


urlpatterns = [
    path("signup", views.sign_up, name="OB-sign_up"),
    path("login/", views.log_in, name="OB-log_in"),
    path("chat/", views.chat, name="OB-chat"),
    path("user/<int:user_id>/", views.get_username, name="OB-get_username")
]