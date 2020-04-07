from django.contrib import admin

from .models import Admin, Ban, Message, OBUser, Room

admin.site.register(OBUser)
admin.site.register(Room)
admin.site.register(Admin)
admin.site.register(Ban)
admin.site.register(Message)
