"""Configuration file for the users module."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AuthConfig(AppConfig):
    """Configuration class of the users module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.users"

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        from collectivo.users.setup import setup

        post_migrate.connect(setup, sender=self)
