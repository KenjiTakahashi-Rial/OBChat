from django.urls import path
from django.conf.urls import url
from . import consumers


websocket_urlpatterns = [
    url(r"^OB/(?P<room_name>[^/]+)/$", consumers.ChatConsumer, name="OB-chat_consumer")
]
