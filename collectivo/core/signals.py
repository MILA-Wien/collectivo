"""Signals of the core extension."""

from django.contrib.auth.models import User
from django.db.models.signals import pre_save


def update_username(sender, instance, **kwargs):
    """Set username to be the same as email."""
    if instance.email and instance.email != instance.username:
        instance.username = instance.email


# Connect the signal to the user model
# This will only apply if the default user model is used
pre_save.connect(update_username, sender=User)
