"""Methods to access the keycloak API."""
from typing import List
from uuid import UUID

from django.conf import settings
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakGetError


class KeycloakAPI:
    """Class that provides methods to access the keycloak API."""

    def __init__(self):
        """Initialize keycloak admin and openid connection."""
        config = settings.COLLECTIVO
        self.admin = KeycloakAdmin(
            server_url=config["keycloak.server_url"],
            realm_name=config["keycloak.realm_name"],
            client_id=config["keycloak.client_id"],
            client_secret_key=config["keycloak.client_secret_key"],
            verify=True,
        )
        self.openid = KeycloakOpenID(
            server_url=config["keycloak.server_url"],
            realm_name=config["keycloak.realm_name"],
            client_id=config["keycloak.client_id"],
            client_secret_key=config["keycloak.client_secret_key"],
        )

    def get_user_fields(self):
        """Return attributes of the user model."""
        return ("first_name", "last_name", "email")

    def get_user_id(self, email):
        """Return user id from keycloak."""
        return self.admin.get_user_id(email)

    def set_user_password(
        self, user_id: UUID, password: str, temporary: bool = True
    ) -> None:
        """Update user password in keycloak."""
        self.admin.set_user_password(user_id, password, temporary=temporary)

    def delete_user(self, user_id):
        """Delete a keycloak user."""
        self.admin.delete_user(user_id)

    def delete_user_by_email(self, email):
        """Delete a keycloak user."""
        user_id = self.get_user_id(email)
        self.delete_user(user_id)

    def __getattr__(self, name):
        """Return attribute from auth manager."""
        return getattr(self.admin, name)

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        email_verified: bool = False,
        exist_ok: bool = False,
    ) -> UUID:
        """Create a keycloak user."""
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "username": email,
            "enabled": True,
            "emailVerified": email_verified,
        }
        user_id = self.admin.create_user(payload, exist_ok=exist_ok)
        return UUID(user_id)

    def update_user(
        self,
        user_id: UUID,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        email_verified: bool = None,
        roles: List[str] = None,
    ) -> None:
        """Update a keycloak user."""
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "emailVerified": email_verified,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        self.admin.update_user(user_id=user_id, payload=payload)
        if roles is not None:
            roles = [
                {"id": self.admin.get_realm_role(role)["id"], "name": role}
                for role in roles
            ]
            self.admin.assign_realm_roles(user_id, roles)

    def get_role_id(self, name: str) -> str:
        """Get a keycloak role."""
        try:
            return self.admin.get_realm_role(name)["id"]
        except KeycloakGetError:
            self.create_role(name=name)
            return self.admin.get_realm_role(name)["id"]

    def create_role(self, name: str) -> None:
        """Create a keycloak role."""
        payload = {"name": name}
        self.admin.create_realm_role(payload)

    def update_role(self, old_name: str, new_name: str) -> None:
        """Update a keycloak role."""
        self.admin.update_realm_role(old_name, {"name": new_name})

    def delete_role(self, name: str) -> None:
        """Delete a keycloak role."""
        self.admin.delete_realm_role(name)
