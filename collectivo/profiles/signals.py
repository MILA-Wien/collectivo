"""Signals of the profiles extension."""
from django.contrib.auth import get_user_model
from django.db.models import signals

from .models import UserProfile


def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when a user is created."""
    profile = UserProfile.objects.get_or_create(user=instance)
    try:
        from collectivo.emails.models import EmailAutomation
        from collectivo.extensions.models import Extension
        extension = Extension.objects.get(name="profiles")
        automation = EmailAutomation.objects.get(
            name="new_user_created", extension=extension
        )
        automation.send(instance, context={"user": instance, "profile": profile})
    except:
        pass


signals.post_save.connect(
    create_user_profile,
    sender=get_user_model(),
    dispatch_uid="create_user_profile",
    weak=False,
)
