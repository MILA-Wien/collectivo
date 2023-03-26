"""Configuration file for the memberships_payments extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ExtensionConfig(AppConfig):
    """Configuration class for the members extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.memberships.payments"
    label = "memberships_payments"
    description = "Connect the memberships and payments extensions."

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        from .setup import setup

        post_migrate.connect(setup, sender=self)
