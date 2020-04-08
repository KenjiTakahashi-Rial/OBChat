from django.conf.urls import url
from .consumers import ChatConsumer


websocket_urlpatterns = [
    url(r"^OB/chat/(?P<room_name>[-\w]+)/$", ChatConsumer, name="OB-chat_consumer")
]
