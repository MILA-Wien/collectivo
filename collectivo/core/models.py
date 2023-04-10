"""Models of the core extension."""
from django.contrib.auth import get_user_model
from django.db import models
from simple_history import register
from simple_history.models import HistoricalRecords

# Create a history for the default user model
register(get_user_model(), app=__package__)


class Collective(models.Model):
    """A collective that uses collectivo."""

    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="collective",
        help_text="The corresponding user for this collective.",
    )

    name = models.CharField(max_length=255)
    history = HistoricalRecords()
