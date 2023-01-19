"""Configuration file for the collectivo package."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize package after database is ready."""
    pass


class CollectivoConfig(AppConfig):
    """Configuration class of the collectivo package."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectivo'

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)
