# Generated by Django 3.0.6 on 2020-07-01 01:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OB', '0022_auto_20200521_1940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='is_revoked',
        ),
    ]