"""Configuration file for the emails_tags extension."""
from django.apps import AppConfig


class ExtensionConfig(AppConfig):
    """Configuration class for the extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.emails.tags"
    label = "emails_tags"
    description = "Connect the emails and tags extensions."
