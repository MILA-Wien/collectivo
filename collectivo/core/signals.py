"""Signals of the core extension."""

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save

from collectivo.extensions.models import Extension

from .models import PermissionGroup


def capitalize(value):
    """Capitalize the first letter of a string."""
    if isinstance(value, str) and len(value) > 0:
        return value[0].upper() + value[1:]
    return value


def user_pre_save(sender, instance, **kwargs):
    """Signal handler for before saving the user model."""

    # Capitalize first and last name
    instance.first_name = capitalize(instance.first_name)
    instance.last_name = capitalize(instance.last_name)

    # Set username to be the same as email
    if instance.email and instance.email != instance.username:
        instance.username = instance.email


def user_post_save(sender, instance, **kwargs):
    """Signal handler for after saving the user model."""

    # Add all users to the all_users group
    all_users = PermissionGroup.objects.get(
        name="all_users",
        extension=Extension.objects.get(name="core"),
        users_custom=False,
    )
    instance.permission_groups.add(all_users)


# Connect the signal to the user model
# This will only apply if the default user model is used
pre_save.connect(user_pre_save, sender=User)
post_save.connect(user_post_save, sender=User)
