"""Setup function of the keycloak auth extension."""
from django.conf import settings
from django.contrib.auth import get_user_model

from collectivo.utils.dev import DEV_USERS

from .api import KeycloakAPI

User = get_user_model()


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    # Activate test users in Keycloak
    if settings.COLLECTIVO["dev.create_test_data"] is True:
        keycloak = KeycloakAPI()
        for first_name in DEV_USERS:
            user = User.objects.get(first_name=first_name)
            uuid = user.keycloak.uuid
            keycloak.set_user_password(uuid, "Test123!", temporary=False)
            if first_name != "user_not_verified":
                keycloak.update_user(uuid, email_verified=True)
