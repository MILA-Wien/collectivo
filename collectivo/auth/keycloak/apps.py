"""Configuration file of the keycloak extension."""
from django.apps import AppConfig

from collectivo.utils.setup import register_setup


class KeycloakConfig(AppConfig):
    """Configuration class of the keycloak extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.auth.keycloak"
    description = "Keycloak connector for collectivo."

    def ready(self):
        """Initialize extension after database is ready."""
        from . import signals  # noqa: F401
        from .setup import setup

        register_setup(setup, self)
