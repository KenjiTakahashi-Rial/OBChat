"""
Manages URL routing for the consumers.

See the Django Channels documentation on Routing for more information.
https://channels.readthedocs.io/en/latest/topics/routing.html
"""

from django.conf.urls import url

from OB.consumers import OBConsumer

URL_PATTERNS = [
    url(r"^OB/chat/(?P<room_name>[-\w]+)/$", OBConsumer, name="OB-room-route"),
    url(r"^OB/private/(?P<username>[-\w]+)/$", OBConsumer, name="OB-private-route")
]
