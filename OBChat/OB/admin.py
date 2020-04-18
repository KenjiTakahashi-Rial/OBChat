"""
Manages which models are visible on the site's admin web-console

See the Django documentation on the admin site for more information.
https://docs.djangoproject.com/en/3.0/ref/contrib/admin/
"""

from django.contrib import admin

from OB.models import Admin, Ban, Message, OBUser, Room

admin.site.register(OBUser)
admin.site.register(Room)
admin.site.register(Admin)
admin.site.register(Ban)
admin.site.register(Message)
