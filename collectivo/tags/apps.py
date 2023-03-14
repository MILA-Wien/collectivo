"""Configuration file for the tags extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class TagsConfig(AppConfig):
    """Configuration class for the tags extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.tags"
    description = "An extension to manage user tags."

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        from .setup import setup

        post_migrate.connect(setup, sender=self)
