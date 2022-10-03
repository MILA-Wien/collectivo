"""Configuration file of the user app."""
from django.apps import AppConfig


class UserConfig(AppConfig):
    """Configuration class of the user app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectivo.user'
