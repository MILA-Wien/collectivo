"""Models of the shift module."""
from django.db import models


class Shift(models.Model):
    """A shift to be done by the collective."""

    shift_title = models.CharField(max_length=30, blank=True)
    first_shift_date = models.DateField(blank=True, null=True)
    shift_type = models.CharField(
        help_text=(
            "Type of shift. Fixed shifts are set automatically every month to "
            "one or many users. Open shifts are not addressed to a user yet."
        ),
        default="fixed",
        max_length=5,
        choices=[
            ("fixed", "fixed"),
            ("open", "open"),
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
    )
    starting_date_time = models.DateTimeField()
    duration = models.FloatField(
        default=3,
    )
    end_date_time = models.DateTimeField()
    required_users = models.PositiveSmallIntegerField(default="2")
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
    )
    additional_info_general = models.TextField(max_length=300)


class GeneralShift(Shift):
    """A shift to be done by the collective."""

    individual_shifts = models.ManyToManyField(
        "IndividualShift",
        related_name="%(class)s_individual_shifts",
        blank=True,
    )  # %(class) to avoid error: https://stackoverflow.com/a/22538875/19932351


class IndividualShift(Shift):
    """A shift to be done by a single user."""

    # comment out for now, to avoid error of unknown private key of ShiftUser
    # assigned_user = models.ForeignKey(
    #     "ShiftUser", on_delete=models.CASCADE, null=True, blank=True
    # )
    assigned_user = models.CharField(max_length=30, blank=True)

    attended = models.BooleanField(
        default=False
    )  # how to require only shift admins to change this?
    additional_info_individual = models.TextField(max_length=300)


class ShiftUser(models.Model):
    """A user that can be assigned to a shift."""

    creator = models.BooleanField(
        default=False
    )  # should be set by keycloak and collectivo
