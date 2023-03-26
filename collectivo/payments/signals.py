"""Signals of the payments extension."""
from django.contrib.auth import get_user_model
from django.db.models import signals

from .models import PaymentProfile


def create_payment_profile(sender, instance, created, **kwargs):
    """Create user profile when a user is created."""
    if created:
        PaymentProfile.objects.create(user=instance)


signals.post_save.connect(
    create_payment_profile,
    sender=get_user_model(),
    dispatch_uid="create_payment_profile",
    weak=False,
)
