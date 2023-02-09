"""A manager for keycloak users and permissions."""
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakPutError
from rest_framework.exceptions import ParseError
from django.conf import settings


class AuthManager:
    """Template for authentication and authorization tools."""

    pass


class KeycloakAuthManager(AuthManager, KeycloakAdmin):
    """Keycloak authentication and authorization tools."""

    def __init__(self):
        """Initialize keycloak admin."""
        config = settings.KEYCLOAK
        super().__init__(
            server_url=config["SERVER_URL"],
            realm_name=config["REALM_NAME"],
            client_id=config["CLIENT_ID"],
            client_secret_key=config["CLIENT_SECRET_KEY"],
            verify=True
        )
        self.openid = KeycloakOpenID(
            server_url=config["SERVER_URL"],
            client_id=config["REALM_NAME"],
            realm_name=config["CLIENT_ID"],
            client_secret_key=config["CLIENT_SECRET_KEY"],
        )

    def get_user_fields(self):
        """Return attributes of the user model."""
        return ('first_name', 'last_name', 'email')

    def create_user(self, first_name, last_name, email,
                    email_verified=False, exist_ok=False):
        """Create a keycloak user."""
        payload = {
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'username': email,
            'enabled': True,
            'emailVerified': email_verified,
        }
        try:
            user = super().create_user(payload, exist_ok=exist_ok)
        except Exception as e:
            raise ParseError(f'Could not create user: {e}')
        return user

    def update_user(self, user_id, first_name=None,
                    last_name=None, email=None,
                    email_verified=None):
        """Update a keycloak user."""
        payload = {
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'emailVerified': email_verified,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        try:
            super().update_user(user_id=user_id, payload=payload)
        except KeycloakPutError as e:
            raise ParseError(f'Could not update user {user_id}: {e}')

    def add_user_to_group(self, user_id, group_name):
        """Add a user to a keycloak group."""
        group_id = self.get_group_by_path(f'/{group_name}')['id']
        self.group_user_add(user_id, group_id)

    def remove_user_from_group(self, user_id, group_name):
        """Remove a user from an authorization group."""
        group_id = self.get_group_by_path(f'/{group_name}')['id']
        self.group_user_remove(user_id, group_id)
