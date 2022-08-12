"""
WSGI config for OBChat project.
It exposes the WSGI callable as a module-level variable named ``application``.

See the Django documentation on wsgi.py for more information.
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OBChat.settings")

application = get_wsgi_application()
