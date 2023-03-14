"""Configuration file of the emails module."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class EmailsConfig(AppConfig):
    """Configuration class of the emails module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.emails"
    description = """Connect collectivo to an email server.
    Can be used by extensions to send automated messages."""

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        from .setup import setup

        post_migrate.connect(setup, sender=self)
