"""Models of the keycloak auth extension."""
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import signals
from keycloak.exceptions import KeycloakGetError

from collectivo.auth.keycloak.api import KeycloakAPI


class KeycloakUser(models.Model):
    """An extension of the user object to connect it to a keycloak account."""

    uuid = models.UUIDField(null=True)
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="keycloak",
    )

    def save(self, *args, **kwargs):
        """Save model and synchronize with keycloak.

        Get and update keycloak user if email exists.
        """
        self.uuid = self.get_keycloak_user()
        if self.uuid is not None:
            self.update_keycloak_user()
        super().save(*args, **kwargs)

    def save_without_sync(self, *args, **kwargs):
        """Save model without synchronizing with keycloak."""
        super().save(*args, **kwargs)

    def get_keycloak_user(self, create=False):
        """Return existing user id or create new auth user."""
        keycloak = KeycloakAPI()

        # If user has uuid, check if the uuid exists on keycloak
        if self.uuid is not None:
            try:
                keycloak.get_user(self.uuid)
                return self.uuid
            except KeycloakGetError:
                pass

        # If user has no uuid, check if user exists on keycloak
        uuid = keycloak.get_user_id(self.user.email)

        # Optional: If user doesn't exist on keycloak, create new keycloak user
        if uuid is None and create:
            uuid = keycloak.create_user(
                self.user.first_name, self.user.last_name, self.user.email
            )

        return uuid

    def update_keycloak_user(self):
        """Update auth user."""
        keycloak = KeycloakAPI()
        keycloak_user = keycloak.get_user(self.uuid)
        keycloak.update_user(
            self.uuid,
            first_name=self.user.first_name
            if keycloak_user["firstName"] != self.user.first_name
            else None,
            last_name=self.user.last_name
            if keycloak_user["lastName"] != self.user.last_name
            else None,
            email=self.user.email
            if keycloak_user["email"] != self.user.email
            else None,
            email_verified=False
            if keycloak_user["email"] != self.user.email
            else None,
        )


def update_keycloak_user(sender, instance, created, **kwargs):
    """Create or update related keycloak user when a django user is changed."""
    try:
        instance.keycloak.save()
    except KeycloakUser.DoesNotExist:
        KeycloakUser.objects.create(user=instance)


signals.post_save.connect(
    update_keycloak_user,
    sender=get_user_model(),
    dispatch_uid="update_keycloak_user",
    weak=False,
)
