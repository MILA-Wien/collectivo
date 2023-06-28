"""Models of the core extension."""
from django.contrib.auth import get_user_model
from django.db import models
from simple_history import register
from simple_history.models import HistoricalRecords

from collectivo.utils.managers import NameManager
from collectivo.utils.models import SingleInstance
from collectivo.utils.texts import EXTENSION_HELP_TEXT

# Create a history for the default user model
User = get_user_model()
register(User, app=__package__)


class CoreSettings(SingleInstance, models.Model):
    """Settings for the core extension."""

    history = HistoricalRecords()

    project_name = models.CharField(
        max_length=255,
        default="My community plattform",
        blank=True,
    )
    project_description = models.TextField(
        blank=True,
    )
    project_logo = models.ImageField(
        upload_to="core/logo/",
        null=True,
        blank=True,
        verbose_name="Project logo (File upload)",
    )
    project_logo_url = models.URLField(
        blank=True,
        verbose_name="Project logo (URL)",
    )

    display_project_name = models.BooleanField(
        default=True,
        verbose_name="Display project name",
    )
    display_project_description = models.BooleanField(
        default=False,
        verbose_name="Display project description",
    )
    display_project_logo = models.BooleanField(
        default=True,
        verbose_name="Display project logo",
    )


class Permission(models.Model):
    """A permission that can be assigned to a group."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.CASCADE,
        related_name="permissions",
        null=True,
        blank=True,
        help_text=EXTENSION_HELP_TEXT,
    )

    history = HistoricalRecords()
    objects = NameManager()

    class Meta:
        """Model settings."""

        unique_together = ("name", "extension")

    def __str__(self):
        """Return the string representation."""
        if self.extension:
            return f"{self.extension}: {self.name}"
        return self.name


class PermissionGroup(models.Model):
    """A group of permissions that can be assigned to users."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        "Permission", related_name="groups", blank=True
    )
    users = models.ManyToManyField(
        User, related_name="permission_groups", blank=True
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.CASCADE,
        related_name="permission_groups",
        null=True,
        blank=True,
        help_text=EXTENSION_HELP_TEXT,
    )
    users_custom = models.BooleanField(
        default=True,
        verbose_name="Custom users",
        help_text="If checked, users can be added to this group manually.",
    )
    perms_custom = models.BooleanField(
        default=True,
        verbose_name="Custom permissions",
        help_text=(
            "If checked, permissions can be added to this group manually."
        ),
    )
    history = HistoricalRecords()
    objects = NameManager()

    class Meta:
        """Model settings."""

        unique_together = ("name", "extension")

    def __str__(self):
        """Return the string representation."""
        if self.extension:
            return f"{self.extension}: {self.name}"
        return self.name
