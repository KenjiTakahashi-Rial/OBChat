# Generated by Django 3.0.3 on 2020-03-22 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OB', '0005_auto_20200322_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='obuser',
            name='birthday',
            field=models.DateField(null=True),
        ),
    ]
