# Generated by Django 3.0.6 on 2020-07-01 01:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OB', '0023_remove_admin_is_revoked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='recipient',
        ),
        migrations.AddField(
            model_name='message',
            name='recipients',
            field=models.ManyToManyField(default=None, null=True, related_name='message_received', to=settings.AUTH_USER_MODEL),
        ),
    ]
