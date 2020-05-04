# Generated by Django 3.0.3 on 2020-05-04 05:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('OB', '0017_auto_20200502_2246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_room', to=settings.AUTH_USER_MODEL),
        ),
    ]
