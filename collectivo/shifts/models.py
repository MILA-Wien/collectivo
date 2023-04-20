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
            "Type of shift. Regular shifts are one time shifts."
            "Repeating shifts can be weekly or monthly."
            "Extra shifts are shifts that are not part of the"
            "regular schedule. Holiday shifts are shifts"
            "that are not part of the regular schedule but are not"
            "extra shifts. Other shifts are shifts that are not"
            "part of the regular schedule and are not extra shifts"
            "and are not holiday shifts."
        ),
        default="fixed",
        max_length=30,
        choices=[
            ("regular", "regular"),
            ("repeating_weekly", "repeating_weekly"),
            ("repeating_monthly", "repeating_monthly"),
            ("extra", "extra"),
            ("holiday", "holiday"),
            ("other", "other"),
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


class ShiftProfile(models.Model):
    """A user that can be assigned to a shift."""

    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="shift_profile",
    )
    shift_points = models.IntegerField(default=0)

    history = HistoricalRecords()


class ShiftAssignment(models.Model):
    """A shift to be done by a single user."""

    assigned_user = models.ForeignKey(
        ShiftProfile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )
    shift = models.ForeignKey(
        Shift, on_delete=models.CASCADE, related_name="assignments"
    )

    # TODO add roles to users and check if user is allowed to change this
    attended = models.BooleanField(default=False)
    additional_info_individual = models.TextField(
        max_length=300,
        blank=True,
        null=True,
        default=None,
    )
    replacement_user = models.ForeignKey(
        ShiftProfile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
        related_name="shift_replacement",
    )
    open_for_replacement = models.BooleanField(default=False)

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
