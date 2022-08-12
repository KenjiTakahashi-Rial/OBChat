# Generated by Django 3.0.3 on 2020-05-03 05:46

import OB.constants
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("OB", "0016_room_group_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="group_type",
            field=models.IntegerField(
                choices=[("Invalid", 0), ("Line", 1), ("Room", 2), ("Private", 3)],
                default=OB.constants.GroupTypes["Room"],
            ),
        ),
    ]
