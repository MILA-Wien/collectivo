"""Models of the payments extension."""
from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords


class PaymentProfile(models.Model):
    """An extension of the user model with payment data."""

    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="payment_profile",
    )

    bank_account_iban = models.CharField(max_length=255, null=True, blank=True)
    bank_account_owner = models.CharField(
        max_length=255, null=True, blank=True
    )
    payment_method = models.CharField(
        choices=[
            ("transfer", "transfer"),
            ("sepa", "sepa"),
        ],
        max_length=30,
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return a string representation of the object."""
        return str(self.user)


class PaymentType(models.Model):
    """A type of payment."""

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class Payment(models.Model):
    """A payment from a user to the collective."""

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="EUR")
    type = models.ForeignKey(
        "PaymentType", on_delete=models.PROTECT, null=True, blank=True
    )
    payer = models.ForeignKey(
        "PaymentProfile", on_delete=models.SET_NULL, null=True, blank=True
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        default="draft",
        choices=[
            ("draft", "draft"),
            ("pending", "pending"),
            ("success", "success"),
            ("canceled", "canceled"),
            ("failure", "failure"),
        ],
    )

    date_due = models.DateField(null=True)
    date_paid = models.DateField(null=True)

    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class Subscription(models.Model):
    """A repetitive payment."""

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    type = models.ForeignKey(
        "PaymentType", on_delete=models.PROTECT, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="EUR")
    payer = models.ForeignKey(
        "PaymentProfile", on_delete=models.SET_NULL, null=True, blank=True
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        default="draft",
        choices=[
            ("draft", "draft"),
            ("paused", "paused"),
            ("active", "active"),
            ("ended", "ended"),
        ],
    )

    date_started = models.DateField(null=True, blank=True)
    date_ended = models.DateField(null=True, blank=True)

    repeat_each = models.IntegerField(default=1)
    repeat_unit = models.CharField(
        max_length=10,
        choices=[
            ("year", "year"),
            ("month", "month"),
            ("week", "week"),
            ("day", "day"),
        ],
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return a string representation of the object."""
        return self.name
