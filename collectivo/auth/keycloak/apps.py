"""Configuration file of the keycloak extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class KeycloakConfig(AppConfig):
    """Configuration class of the keycloak extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.auth.keycloak"
    description = "Keycloak connector for collectivo."
