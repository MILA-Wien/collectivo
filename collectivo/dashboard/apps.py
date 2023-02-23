"""Configuration file for the dashboard extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate

from collectivo.version import __version__


class DashboardConfig(AppConfig):
    """Configuration class for the dashboard extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.dashboard"
    description = """An extension to provide a starting page where other
    extensions can display tiles."""

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        from .setup import setup

        post_migrate.connect(setup, sender=self)
