# Generated by Django 3.0.3 on 2020-03-14 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("OB", "0003_auto_20200222_1932"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="message",
            name="is_edited",
            field=models.BooleanField(default=False),
        ),
    ]
