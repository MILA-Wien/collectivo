"""Setup function of the keycloak auth extension."""
from django.conf import settings
from django.contrib.auth import get_user_model

from collectivo.utils.dev import DEV_USERS

from .api import KeycloakAPI

User = get_user_model()


def setup():
    """Initialize extension after database is ready."""

    # Create missing keycloak connectors
    users = User.objects.filter(keycloak__isnull=True)
    for user in users:
        user.save()

    # Activate test users in Keycloak
    if settings.COLLECTIVO["example_data"] is True:
        keycloak = KeycloakAPI()
        for first_name in DEV_USERS:
            user = User.objects.get(email=f"test_{first_name}@example.com")
            uuid = user.keycloak.get_keycloak_user(create=True)
            keycloak.set_user_password(uuid, "Test123!", temporary=False)
            if first_name != "user_not_verified":
                keycloak.update_user(uuid, email_verified=True)
