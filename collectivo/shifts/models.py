"""Models of the shift module."""
import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.postgres.fields import ArrayField
from django.db import models


class GeneralShift(models.Model):
    """A shift to be done by the collective."""

    shift_title = models.CharField(max_length=30, blank=True)
    first_shift_date = models.DateField(blank=True, null=True)
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
    shift_starting_time = models.TimeField(default=datetime.now())
    duration = models.FloatField(
        default=3,
    )
    shift_end_time = models.TimeField(default=datetime.now() + relativedelta(hours=3))
    required_users = models.PositiveSmallIntegerField(default=2)
    shift_day = models.CharField(
        help_text=(
            "Shift days are necessary for fixed shifts to register"
            "i.e. every monday on Week A"
        ),
        max_length=10,
        default="Monday",
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
    starting_search_date = models.DateField(blank=True, null=True)
    ending_search_date = models.DateField(blank=True, null=True)
    shift_date_list = (
        ArrayField(
            models.DateField(blank=True, null=True),
        ),
    )
    shift_user_list = ArrayField(
        models.CharField(max_length=30, blank=True, null=True),
    )
    shift_appointment = models.DateTimeField(blank=True, null=True)


class IndividualShift(models.Model):
    """A shift to be done by a single user."""

    assigned_user = models.ForeignKey(
        "ShiftUser",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )
    general_shift = models.ForeignKey(GeneralShift, on_delete=models.CASCADE)

    # TODO add roles to users and check if user is allowed to change this
    attended = models.BooleanField(default=False)
    additional_info_individual = models.TextField(max_length=300)


class ShiftUser(models.Model):
    """A user that can be assigned to a shift."""

    # TODO should be set by keycloak and collectivo
    username = models.CharField(max_length=30, blank=True)
    creator = models.BooleanField(default=False)
