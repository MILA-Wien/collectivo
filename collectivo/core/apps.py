"""apps contains the core app configuration."""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """CoreConfig contains the configuration for the core app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
