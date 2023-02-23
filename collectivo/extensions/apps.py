"""Configuration file for the extensions module.."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ExtensionsConfig(AppConfig):
    """Configuration class of the extensions module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.extensions"
    description = "Manage extensions of collectivo."

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        from .setup import setup

        post_migrate.connect(setup, sender=self)
