"""Configuration file for the profiles extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ProfilesConfig(AppConfig):
    """Configuration class for the profiles extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.profiles"
    description = "Store basic data about users."

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        from . import signals  # noqa: F401
        from .setup import setup

        post_migrate.connect(setup, sender=self)
