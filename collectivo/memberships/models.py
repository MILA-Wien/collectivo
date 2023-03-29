"""Models of the memberships extension."""
from datetime import date

from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords

from collectivo.utils.managers import NameManager

# --------------------------------------------------------------------------- #
# Membership types ---------------------------------------------------------- #
# --------------------------------------------------------------------------- #


class MembershipType(models.Model):
    """A type of membership."""

    objects = NameManager()

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    # TODO: Validation for this field
    statuses = models.ManyToManyField(
        "MembershipStatus",
        help_text="The statuses that a membership of this type can have.",
        blank=True,
    )

    has_shares = models.BooleanField(
        default=False,
        help_text="Whether users need to buy shares to become members.",
    )
    shares_amount_per_share = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The amount of money that has to be paid per share.",
    )
    shares_number_custom = models.BooleanField(
        default=False,
        help_text="Whether members can choose a custom number of shares.",
    )
    shares_number_custom_min = models.IntegerField(
        null=True,
        blank=True,
        help_text="The minimum number of shares for custom numbers of shares.",
    )
    shares_number_custom_max = models.IntegerField(
        null=True,
        blank=True,
        help_text="The maximum number of shares for custom numbers of shares.",
    )
    shares_number_standard = models.IntegerField(
        null=True, blank=True, help_text="The default number of shares."
    )
    shares_number_social = models.IntegerField(
        null=True,
        blank=True,
        help_text="A reduced number of shares.",
    )

    has_fees = models.BooleanField(default=False)
    fees_amount_custom = models.BooleanField(default=False)
    fees_amount_custom_min = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )
    fees_amount_custom_max = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )
    fees_amount_standard = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )
    fees_amount_social = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )
    fees_repeat_each = models.IntegerField(default=1)
    fees_repeat_unit = models.CharField(
        max_length=20,
        default="year",
        choices=[
            ("year", "year"),
            ("month", "month"),
            ("week", "week"),
            ("day", "day"),
        ],
    )

    currency = models.CharField(
        max_length=3,
        default="EUR",
        help_text="The currency used for fees and shares.",
    )

    comembership_of = models.ForeignKey(
        "MembershipType", null=True, blank=True, on_delete=models.CASCADE
    )
    comembership_max = models.IntegerField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        """Return string representation."""
        return self.name


class MembershipStatus(models.Model):
    """A status of a membership (sub-type)."""

    objects = NameManager()

    name = models.CharField(unique=True, max_length=255)
    history = HistoricalRecords()

    def __str__(self):
        """Return string representation."""
        return self.name


# --------------------------------------------------------------------------- #
# Memberships --------------------------------------------------------------- #
# --------------------------------------------------------------------------- #


class Membership(models.Model):
    """A membership of a user."""

    class Meta:
        """Meta settings."""

        unique_together = ("number", "type")

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    number = models.IntegerField(verbose_name="Membership number")

    date_started = models.DateField(null=True, blank=True, default=date.today)
    date_cancelled = models.DateField(null=True, blank=True)
    date_ended = models.DateField(null=True, blank=True)
    type = models.ForeignKey(
        "MembershipType", on_delete=models.PROTECT, related_name="memberships"
    )
    status = models.ForeignKey(
        "MembershipStatus", null=True, blank=True, on_delete=models.PROTECT
    )

    # Optional depending on membership type
    shares_signed = models.PositiveIntegerField(default=0)
    shares_paid = models.PositiveIntegerField(default=0)
    fees_amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0
    )
    comembership_of = models.ForeignKey(
        "Membership", blank=True, null=True, on_delete=models.CASCADE
    )

    history = HistoricalRecords()

    def generate_membership_number(self):
        """Generate a unique membership number."""
        highest_number = (
            Membership.objects.filter(type=self.type).order_by("number").last()
        )
        return 1 if highest_number is None else highest_number.number + 1

    def save(self, *args, **kwargs):
        """Save membership and create payments."""
        if self.number is None:
            self.number = self.generate_membership_number()
        super().save()

    def __str__(self):
        """Return string representation."""
        return (
            f"{self.user.first_name} {self.user.last_name} "
            f"({self.type.name})"
        )
