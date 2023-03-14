"""Models of the core extension."""
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import signals

from collectivo.auth.keycloak.api import KeycloakAPI


class KeycloakUser(models.Model):
    """An extension of the user object to connect it to a keycloak account."""

    uuid = models.UUIDField(primary_key=True)
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="keycloak",
    )

    def save(self, *args, **kwargs):
        """Save model and synchronize with keycloak.

        Get or create keycloak user if a new instance is created.
        Update keycloak user if an existing instance is updated.
        """
        if self.uuid is None:
            self.uuid = self.get_or_create_keycloak_user()
        else:
            self.update_keycloak_user()
        super().save(*args, **kwargs)

    def save_without_sync(self, *args, **kwargs):
        """Save model without synchronizing with keycloak."""
        super().save(*args, **kwargs)

    def get_or_create_keycloak_user(self):
        """Return existing user id or create new auth user."""
        auth = KeycloakAPI()
        uuid = auth.get_user_id(self.user.email)
        if uuid is None:
            uuid = auth.create_user(
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
        if instance.email:
            KeycloakUser.objects.create(user=instance)


def delete_keycloak_user(sender, instance, **kwargs):
    """Delete related keycloak user when a django user is deleted."""
    try:
        instance.keycloak.delete()
    except KeycloakUser.DoesNotExist:
        pass


signals.post_save.connect(
    update_keycloak_user,
    sender=get_user_model(),
    dispatch_uid="update_keycloak_user",
    weak=False,
)

signals.post_delete.connect(
    delete_keycloak_user,
    sender=get_user_model(),
    dispatch_uid="delete_keycloak_user",
    weak=False,
)
