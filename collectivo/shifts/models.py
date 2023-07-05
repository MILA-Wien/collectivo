"""Models of the shift module."""
from datetime import date

from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords

from collectivo.utils.managers import NameManager

from .abcd import get_abcd_occurences


class Shift(models.Model):
    """A timed event that can have multiple occurences."""

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    starting_time = models.TimeField(blank=True, null=True)
    ending_time = models.TimeField(blank=True, null=True)

    shift_points = models.FloatField(
        default=1,
        help_text="Number of points that can be gained by doing this shift.",
    )
    notes = models.TextField(blank=True, null=True, help_text="")

    repeat = models.CharField(
        max_length=30,
        default="none",
        choices=[
            ("none", "No repetition"),
            ("abcd", "Every fourth week (ABCD)"),
        ],
    )

    # For shifts without repetition
    date = models.DateField(blank=True, null=True)

    # For shifts with repetition
    repeat_start = models.DateField(blank=True, null=True)
    repeat_end = models.DateField(blank=True, null=True)

    # For shifts with ABCD repetition
    abcd_week = models.CharField(
        help_text=(
            "The weeks of a year are divided into four groups: A, B, C, D"
        ),
        verbose_name="Shift week",
        max_length=1,
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ],
        blank=True,
        null=True,
    )
    abcd_day = models.CharField(
        help_text=(
            "The day of the week the shift takes place, "
            "i.e. every Monday on Week A."
        ),
        verbose_name="Shift day",
        max_length=10,
        default="MO",
        choices=[
            ("MO", "Monday"),
            ("TU", "Tuesday"),
            ("WE", "Wednesday"),
            ("TH", "Thursday"),
            ("FR", "Friday"),
            ("SA", "Saturday"),
            ("SU", "Sunday"),
        ],
        blank=True,
        null=True,
    )

    def get_next_occurence(self):
        """Get the next occurence of the shift."""
        if self.repeat == "none":
            return self.date
        if self.repeat == "abcd":
            return self.get_next_abcd_occurence()

    def get_next_abcd_occurence(self):
        """Get the next occurence of the shift with ABCD repetition."""
        return list(
            get_abcd_occurences(
                self.abcd_week, self.abcd_day, date.today(), count=1
            )
        )[0].strftime("%Y-%m-%d")

    def __str__(self):
        """Return the name of the shift."""
        return self.name


class ShiftProfile(models.Model):
    """User profile for the shifts extension."""

    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="shift_profile",
    )
    type = models.CharField(
        max_length=30,
        default="none",
        choices=[
            ("jumper", "Jumper: Do shifts without repetition."),
            ("abcd", "Regular: Do a shift that repeats every four weeks."),
        ],
    )
    shift_points = models.IntegerField(default=0)

    history = HistoricalRecords()


class ShiftSlot(models.Model):
    """Assignment of a user to a shift."""

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
        related_name="shift_slots",
    )
    shift = models.ForeignKey(
        Shift, on_delete=models.CASCADE, related_name="slots"
    )

    history = HistoricalRecords()


class ShiftSettings(models.Model):
    """Settings for the shift module."""

    shift_weeks = models.PositiveSmallIntegerField(default=4)
    shift_per_month = models.PositiveSmallIntegerField(default=1)
    shift_hours = models.PositiveSmallIntegerField(default=3)
    shift_points_per_shift = models.PositiveSmallIntegerField(default=1)
    # TODO add shift points per role and shift type
    shift_points_period_in_days = models.PositiveSmallIntegerField(default=30)
    shift_points_per_period = models.PositiveSmallIntegerField(default=1)
    shift_points_subsbtraction_day = models.PositiveSmallIntegerField(
        default=1
    )
    disable_shift_points = models.BooleanField(default=True)
    disable_attendance = models.BooleanField(default=True)
    disable_shift_replacement = models.BooleanField(default=True)

    history = HistoricalRecords()
