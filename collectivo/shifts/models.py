"""Models of the user experience module."""
from django.db import models


class GeneralShift(models.Model):
    """A shift to be done by the collective."""

    first_shift_date = models.DateField(max_length=30)
    shift_type = models.CharField(
        help_text=(
            "Type of shift. Fixed shifts are set automatically every month to "
            "one or many users. Open shifts are not addressed to a user yet."
        ),
        max_length=20,
        default="fixed",
        choices=[
            ("fixed", "fixed"),
            ("open", "open"),
        ],
    )
    shift_week = models.CharField(
        help_text="A month is divided in four shift weeks: A, B, C, D",
        max_length=2,
        default="A",
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ],
    )
    starting_time = models.DateField(max_length=30)
    duration = models.FloatField(
        default=3,
    )
    required_users = models.IntegerField()
    shift_day = models.CharField(
        help_text=(
            "Shift days are necessary for fixed shifts to register"
            "i.e. every monday on Week A"
        ),
        max_length=20,
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
    individual_shifts = models.ManyToManyField("IndividualShift")


class IndividualShift(models.Model):
    assigned_user = models.ForeignKey("ShiftUser", on_delete=models.CASCADE)
    requirement = models.ManyToManyField("ShiftRequirement")


class ShiftRequirement(models.Model):
    pass


class ShiftUser(models.Model):
    pass
