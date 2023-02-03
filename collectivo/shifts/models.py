"""Models of the shift module."""
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
    starting_time = models.DateTimeField()
    duration = models.FloatField(
        default=3,
    )
    end_time = models.DateTimeField()
    required_users = models.IntegerField(default=2)
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
    individual_shifts = models.ManyToManyField(
        "IndividualShift", related_name="%(class)s_individual_shifts", blank=True
    )  # adding class to avoid error: https://stackoverflow.com/a/22538875/19932351
    additional_info_general = models.TextField(max_length=300)


class IndividualShift(GeneralShift):
    # to access attributes from parent class, read:
    # https://stackoverflow.com/a/19143342/19932351
    assigned_user = models.ForeignKey("ShiftUser", on_delete=models.CASCADE)
    user_has_attended = models.BooleanField(
        default=False
    )  # how to require only shift admins to change this?
    additional_info_individual = models.TextField(max_length=300)


class ShiftUser(models.Model):
    shift_creator = models.BooleanField(
        default=False
    )  # should be set by keycloak and collectivo
