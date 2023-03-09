"""Configuration file for the payments extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate

from collectivo.version import __version__


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    pass


class PaymentsConfig(AppConfig):
    """Configuration class for the payments extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.payments"

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)
