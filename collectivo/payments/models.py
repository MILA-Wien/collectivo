"""Models of the payments module."""
from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords


class PaymentProfile(models.Model):
    """An extension of the user model with payment data."""

    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="payments",
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


class Payment(models.Model):
    """A payment."""

    name = models.CharField(max_length=255)
    purpose = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        "PaymentProfile", on_delete=models.SET_NULL, null=True, blank=True
    )

    status = models.CharField(
        max_length=10,
        default="draft",
        choices=[
            ("draft", "draft"),
            ("pending", "pending"),
            ("success", "success"),
            ("failure", "failure"),
        ],
    )

    created = models.DateTimeField(auto_now_add=True)
    payed = models.DateTimeField(null=True)

    subscription = models.ForeignKey(
        "Subscription", on_delete=models.SET_NULL, null=True, blank=True
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class Subscription(models.Model):
    """A repetitive payment."""

    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        "PaymentProfile", on_delete=models.SET_NULL, null=True, blank=True
    )

    starting_date = models.DateField()
    ending_date = models.DateField(null=True)

    repeat_each = models.IntegerField()
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
