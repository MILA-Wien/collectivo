"""Models of the authentication module."""
from uuid import UUID

from django.conf import settings
from django.db import models
from django.db.models.manager import BaseManager, EmptyManager, Manager

from collectivo.users.services import AuthService


class User(models.Model):
    """A user that corresponds to a user of the authentication service."""

    user_id = models.UUIDField(primary_key=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    roles = models.ManyToManyField("Role", blank=True)
    created = models.DateField(auto_now_add=True)
    is_authenticated = True

    @property
    def is_superuser(self):
        """Return True if user is superuser."""
        return self.roles.filter(name="superuser").exists()

    def __str__(self):
        """Return string representation."""
        return f"{self.first_name} {self.last_name} ({self.email})"

    def save(self, *args, **kwargs):
        """Save model and synchronize with auth service.

        Get or create auth user if a new instance is created.
        Update auth user if an existing instance is updated."""
        if self.user_id is None:
            self.user_id = self.get_or_create_auth_user()
        else:
            self.update_auth_user()
        super().save(*args, **kwargs)

    def save_without_sync(self, *args, **kwargs):
        """Save model without synchronizing with auth service."""
        super().save(*args, **kwargs)

    def get_or_create_auth_user(self):
        """Return existing user id or create new auth user."""
        auth = AuthService()
        user_id = auth.get_user_id(self.email)
        if user_id is None:
            user_id = auth.create_user(
                self.first_name, self.last_name, self.email
            )
        return user_id

    def update_auth_user(self):
        """Update auth user."""
        auth_service = AuthService()
        user = auth_service.get_user(self.user_id)
        auth_service.update_user(
            self.user_id,
            first_name=self.first_name
            if user.first_name != self.first_name
            else None,
            last_name=self.last_name
            if user.last_name != self.last_name
            else None,
            email=self.email if user.email != self.email else None,
            email_verified=False if user.email != self.email else None,
            roles=[role.name for role in self.roles.all()],
        )

    def set_email_verified(self, email_verified: bool):
        """Set whether the email of auth user is verified."""
        auth = AuthService()
        auth.update_user(self.user_id, email_verified=email_verified)

    def set_password(self, password, temporary: bool = True):
        """Set password for auth user."""
        auth = AuthService()
        auth.set_user_password(self.user_id, password, temporary)

    def get_token(self, password):
        """Return token for auth user."""
        auth = AuthService()
        return auth.get_token(self.email, password)

    def has_role_or_is_superuser(self, role_name: str):
        """Return True if user has role or is superuser."""
        return self.is_superuser or self.roles.filter(name=role_name).exists()


class Role(models.Model):
    """A role that can be assigned to users
    (synced with auth service)."""

    role_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def get_or_create_role(self):
        """Return existing role id or create new role."""
        auth_service = AuthService()
        role_id = auth_service.get_role_id(self.name)
        if role_id is None:
            role_id = auth_service.create_realm_role(self.name)
        return role_id

    def update_role(self):
        """Update role."""
        auth_service = AuthService()
        auth_service.update_realm_role(self.role_id, self.name)

    def save(self, *args, **kwargs):
        """Save model and synchronize with auth service."""
        if self.role_id is None:
            self.role_id = self.get_or_create_role()
        else:
            self.update_role()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return string representation."""
        return f"Role ({self.name})"


class AnonymousUser:
    """Representation for anonymous users."""

    user_id: UUID = None
    email: str = None
    first_name: str = None
    last_name: str = None
    roles: list = EmptyManager(Role)
    created: str = None
    is_authenticated: bool = False
    is_superuser: bool = False

    def __str__(self):
        """Return string representation."""
        return "Anonymous User"

    def has_role_or_is_superuser(self, role_name: str):
        """Return True if user has role or is superuser."""
        return False


class SuperUser:
    """Representation for internal superusers."""

    user_id: UUID = None
    email: str = None
    first_name: str = None
    last_name: str = None
    roles: list = EmptyManager(Role)
    created: str = None
    is_authenticated: bool = True
    is_superuser: bool = True

    def __str__(self):
        """Return string representation."""
        return "Anonymous User"

    def has_role_or_is_superuser(self, role_name: str):
        """Return True if user has role or is superuser."""
        return True
