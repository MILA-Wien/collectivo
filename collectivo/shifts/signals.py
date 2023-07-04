"""Signals of the shifts extension."""
from django.contrib.auth import get_user_model
from django.db.models import signals

from .models import ShiftProfile


def create_shift_profile(sender, instance, created, **kwargs):
    """Create profile when a user does not have one."""

    ShiftProfile.objects.get_or_create(user=instance)


signals.post_save.connect(
    create_shift_profile,
    sender=get_user_model(),
    dispatch_uid="create_shift_profile",
    weak=False,
)
