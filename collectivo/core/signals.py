"""Signals of the core extension."""

from django.contrib.auth.models import User
from django.db.models.signals import pre_save


def capitalize(value):
    """Capitalize the first letter of a string."""
    if isinstance(value, str) and len(value) > 0:
        return value[0].upper() + value[1:]
    return value


def update_username(sender, instance, **kwargs):
    """Set username to be the same as email and capitalize names."""
    instance.first_name = capitalize(instance.first_name)
    instance.last_name = capitalize(instance.last_name)
    if instance.email and instance.email != instance.username:
        instance.username = instance.email


# Connect the signal to the user model
# This will only apply if the default user model is used
pre_save.connect(update_username, sender=User)
