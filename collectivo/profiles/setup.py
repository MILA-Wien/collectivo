"""Setup function for the profiles extension."""
from django.conf import settings
from django.contrib.auth import get_user_model

from collectivo.extensions.models import Extension
from collectivo.utils.dev import DEV_MEMBERS

from . import models
from .apps import ProfilesConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.register(
        name=ProfilesConfig.name,
        description=ProfilesConfig.description,
        built_in=True,
    )

    if settings.COLLECTIVO["dev.create_test_data"] is True:
        for first_name in DEV_MEMBERS:
            email = f"test_{first_name}@example.com"
            user = get_user_model().objects.get(email=email)
            models.UserProfile.objects.get_or_create(user=user)
