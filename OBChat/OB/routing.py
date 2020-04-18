"""
Manages URL routing for the consumers.

See the Django Channels documentation on Routing for more information.
https://channels.readthedocs.io/en/latest/topics/routing.html
"""

from django.conf.urls import url
from .consumers import OBConsumer

websocket_urlpatterns = [
    url(r"^OB/chat/(?P<room_name>[-\w]+)/$", OBConsumer, name="OB-consumer")
]
