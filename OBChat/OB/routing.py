from django.conf.urls import url
from .consumers import OBConsumer


websocket_urlpatterns = [
    url(r"^OB/chat/(?P<room_name>[-\w]+)/$", OBConsumer, name="OB-consumer")
]
