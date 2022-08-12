"""
Manages URL routing for the Consumers.

See the Django Channels documentation on Routing for more information.
https://channels.readthedocs.io/en/latest/topics/routing.html
"""

from django.urls import re_path

from OB.consumers import OBConsumer

URL_PATTERNS = [
    re_path(r"^OB/chat/(?P<room_name>[-\w]+)/$", OBConsumer.as_asgi(), name="OB-room-route"),
    re_path(r"^OB/private/(?P<username>[-\w]+)/$", OBConsumer.as_asgi(), name="OB-private-route"),
]
