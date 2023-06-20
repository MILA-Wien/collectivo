# Generated by Django 4.1.9 on 2023-06-20 07:47

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('memberships', '0004_historicalmembershiptype_enable_registration_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together={('user', 'type'), ('number', 'type')},
        ),
    ]
