"""Configuration file for the direktkredit extension."""

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class DirektkreditConfig(AppConfig):
    """Configuration class for the direktkredit extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.direktkredit"
    description = "Integration with the direct loan system from habidat."

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        from .setup import setup

        post_migrate.connect(setup, sender=self)
