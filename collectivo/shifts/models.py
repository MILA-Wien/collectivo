"""Models of the shift module."""
from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords


class Shift(models.Model):
    """A shift to be done by the collective."""

    shift_title = models.CharField(max_length=30, blank=True)
    shift_starting_date = models.DateField(blank=True, null=True)
    shift_ending_date = models.DateField(blank=True, null=True)
    shift_type = models.CharField(
        help_text=(
            "Type of shift. Either shifts happen on a regular basis. "
            "Or they are unique and happen only once."
        ),
        default="fixed",
        max_length=30,
        choices=[
            ("regular", "regular"),
            ("unique", "unique"),
        ],
    )
    shift_week = models.CharField(
        help_text="A month is divided in four shift weeks: A, B, C, D",
        max_length=1,
        default="A",
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ],
        blank=True,
        null=True,
    )
    shift_starting_time = models.TimeField(
        blank=True,
        null=True,
    )
    shift_ending_time = models.TimeField(blank=True, null=True)
    required_users = models.PositiveSmallIntegerField(default=2)
    shift_day = models.CharField(
        help_text=(
            "Shift days are necessary for fixed shifts to register"
            "i.e. every monday on Week A"
        ),
        max_length=10,
        default="MO",
        choices=[
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
            ("Sunday", "Sunday"),
        ],
        blank=True,
        null=True,
    )
    additional_info_general = models.TextField(
        max_length=300,
        blank=True,
        null=True,
    )

    history = HistoricalRecords()


class ShiftAssignment(models.Model):
    """A shift to be done by a single user."""

    assigned_user = models.ForeignKey(
        "ShiftProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    # TODO add roles to users and check if user is allowed to change this
    attended = models.BooleanField(default=False)
    additional_info_individual = models.TextField(max_length=300)

    history = HistoricalRecords()


class ShiftProfile(models.Model):
    """A user that can be assigned to a shift."""

    user = models.OneToOneField(
        get_user_model(), primary_key=True, on_delete=models.CASCADE
    )

    history = HistoricalRecords()
