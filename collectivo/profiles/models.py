"""Models of the profiles extension."""
from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords


class UserProfile(models.Model):
    """Extension of the user model with a user profile."""

    # User account
    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Personal data
    person_type = models.CharField(
        max_length=50,
        null=True,
        choices=[
            ("natural", "natural"),
            ("legal", "legal"),
        ],
    )
    gender = models.CharField(
        max_length=50,
        null=True,
        choices=[
            ("diverse", "diverse"),
            ("female", "female"),
            ("male", "male"),
        ],
    )
    address_street = models.CharField(max_length=255)
    address_number = models.CharField(max_length=255)
    address_stair = models.CharField(max_length=255, blank=True)
    address_door = models.CharField(max_length=255, blank=True)
    address_postcode = models.CharField(max_length=255)
    address_city = models.CharField(max_length=255)
    address_country = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, blank=True)

    # Personal data (only for natural person)
    birthday = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)

    # Personal data (only for legal person)
    legal_name = models.CharField(max_length=255, blank=True)
    legal_type = models.CharField(max_length=255, blank=True)
    legal_id = models.CharField(max_length=255, blank=True)

    # Admin data
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    def __str__(self):
        """Return string representation."""
        return f"{self.user.first_name} {self.user.last_name}"
