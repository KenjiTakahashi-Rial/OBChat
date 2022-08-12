"""
ASGI config for OBChat project.
Exposes the ASGI callable as a module-level variable named ``application``.

See the Django documentation on asgi.py for more information.
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OBChat.settings")

application = get_asgi_application()
