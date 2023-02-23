"""Manager class to connect collectivo to an authentication service."""
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import (
    KeycloakPutError,
    KeycloakDeleteError,
    KeycloakGetError,
    KeycloakError,
    KeycloakPostError,
)
from collectivo.users.exceptions import (
    AuthDeleteError,
    AuthGetError,
    AuthUpdateError,
    AuthCreateError,
)
from django.conf import settings
from collectivo.utils import get_object_from_settings
from uuid import UUID
from typing import List
from dataclasses import dataclass


@dataclass
class AuthUser:
    """Representation for users of the authentication service."""

    user_id: UUID
    email: str
    email_verified: bool
    first_name: str
    last_name: str


@dataclass
class AuthToken:
    """Representation for tokens of the authentication service."""

    access_token: str
    refresh_token: str = None
    access_expires_in: int = None
    refresh_expires_in: int = None


class AuthService:
    """Representation of the authentication service."""

    def __init__(self):
        """Initialize auth manager as defined in settings."""
        self._manager = get_object_from_settings("auth.service")()

    def get_user_id(self, email: str) -> UUID:
        """Return user id from auth service."""
        return self._manager.get_user_id(email)

    def get_user(self, user_id: UUID) -> AuthUser:
        """Return user from auth service."""
        return self._manager.get_user(user_id)

    def get_user_by_email(self, email: str) -> AuthUser:
        """Return user from auth service."""
        return self._manager.get_user_by_email(email)

    def get_token(self, email: str, password: str) -> AuthToken:
        """Return token from auth service."""
        return self._manager.get_token(email, password)

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        email_verified: bool = False,
    ) -> str:
        """Create user in auth service. Returns user id."""
        return self._manager.create_user(
            first_name, last_name, email, email_verified
        )

    def update_user(
        self,
        user_id: UUID,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        email_verified: bool = None,
        roles: List[str] = None,
    ) -> None:
        """Update user in auth service."""
        self._manager.update_user(
            user_id, first_name, last_name, email, email_verified, roles
        )

    def set_user_password(
        self, user_id: UUID, password: str, temporary: bool = True
    ) -> None:
        """Update user password in auth service."""
        self._manager.set_user_password(user_id, password, temporary)

    def delete_user(self, user_id: UUID) -> None:
        """Delete user from auth service."""
        self._manager.delete_user(user_id)

    def __getattr__(self, name):
        """Return attribute from auth manager."""
        return getattr(self._manager, name)


class KeycloakAuthService:
    """Keycloak authentication service."""

    def __init__(self):
        """Initialize keycloak admin."""
        config = settings.KEYCLOAK
        self.admin = KeycloakAdmin(
            server_url=config["SERVER_URL"],
            realm_name=config["REALM_NAME"],
            client_id=config["CLIENT_ID"],
            client_secret_key=config["CLIENT_SECRET_KEY"],
            verify=True,
        )
        self.openid = KeycloakOpenID(
            server_url=config["SERVER_URL"],
            client_id=config["REALM_NAME"],
            realm_name=config["CLIENT_ID"],
            client_secret_key=config["CLIENT_SECRET_KEY"],
        )

    def get_user_fields(self):
        """Return attributes of the user model."""
        return ("first_name", "last_name", "email")

    def get_user(self, user_id) -> AuthUser:
        """Return user from keycloak."""
        user_rep = self.admin.get_user(user_id)
        return AuthUser(
            user_id=user_id,
            email=user_rep["email"],
            email_verified=user_rep["emailVerified"],
            first_name=user_rep["firstName"],
            last_name=user_rep["lastName"],
        )

    def get_user_by_email(self, email: str) -> AuthUser:
        """Return user from keycloak."""
        user_id = self.get_user_id(email)
        return self.get_user(user_id)

    def get_token(self, email: str, password: str) -> str:
        """Return token from keycloak."""
        try:
            token = self.openid.token(email, password)
        except Exception as e:
            raise AuthGetError(e)
        return AuthToken(
            access_token=token["access_token"],
            refresh_token=token["refresh_token"],
            access_expires_in=token["expires_in"],
            refresh_expires_in=token["refresh_expires_in"],
        )

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
        try:
            self.admin.delete_user(user_id)
        except KeycloakDeleteError as e:
            raise AuthDeleteError(e.error_message)

    def __getattr__(self, name):
        """Return attribute from auth manager."""
        return getattr(self.admin, name)

    def create_user(
        self,
        first_name,
        last_name,
        email,
        email_verified=False,
        exist_ok=False,
    ):
        """Create a keycloak user."""
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "username": email,
            "enabled": True,
            "emailVerified": email_verified,
        }
        try:
            user = self.admin.create_user(payload, exist_ok=exist_ok)
        except Exception as e:
            raise AuthCreateError(f"Could not create user: {e}")
        return user

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
        try:
            self.admin.update_user(user_id=user_id, payload=payload)
            if roles is not None:
                roles = [
                    {"id": self.admin.get_realm_role(role)["id"], "name": role}
                    for role in roles
                ]
                self.admin.assign_realm_roles(user_id, roles)
        except KeycloakPutError as e:
            raise AuthUpdateError(f"Could not update user {user_id}: {e}")

    def get_role_id(self, name: str) -> str:
        """Get a keycloak role."""
        try:
            return self.admin.get_realm_role(name)["id"]
        except KeycloakGetError as e:
            raise AuthGetError(f"Could not get id of role {name}: {e}")

    def create_role(self, name: str) -> None:
        """Create a keycloak role."""
        payload = {"name": name}
        try:
            self.admin.create_realm_role(payload)
        except KeycloakPostError as e:
            raise AuthCreateError(f"Could not create role {name}: {e}")

    def update_role(self, name: str, new_name: str) -> None:
        """Update a keycloak role."""
        try:
            self.admin.update_realm_role(name, {"name": new_name})
        except KeycloakPutError as e:
            raise AuthUpdateError(f"Could not update role {name}: {e}")

    def delete_role(self, name: str) -> None:
        """Delete a keycloak role."""
        try:
            self.admin.delete_realm_role(name)
        except KeycloakDeleteError as e:
            raise AuthDeleteError(f"Could not delete role {name}: {e}")
