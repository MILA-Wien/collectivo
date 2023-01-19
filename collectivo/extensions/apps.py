"""Configuration file for the extensions module.."""
from django.apps import AppConfig


class ExtensionsConfig(AppConfig):
    """Configuration class of the extensions module."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectivo.extensions'
