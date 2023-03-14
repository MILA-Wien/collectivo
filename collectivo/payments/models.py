"""Models of the payments module."""
from django.contrib.auth import get_user_model
from django.db import models


# TODO: How to manage the payment methods? Some need iban, some something else
class PaymentMethod(models.Model):
    """A payment method."""

    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        """Return a string representation of the object."""
        return f"PaymentMethod ({self.name})"


class PaymentProfile(models.Model):
    """An extension of the user model with payment data."""

    user = models.OneToOneField(
        get_user_model(), primary_key=True, on_delete=models.CASCADE
    )

    bank_account_iban = models.CharField(max_length=255, null=True, blank=True)
    bank_account_owner = models.CharField(
        max_length=255, null=True, blank=True
    )
    payment_method = models.ForeignKey(
        "PaymentMethod",
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        """Return a string representation of the object."""
        return f"PaymentUser ({self.user_id})"


class Payment(models.Model):
    """A payment."""

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

    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    profile = models.ForeignKey(
        "PaymentProfile", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        """Return a string representation of the object."""
        return f"Payment ({self.name})"


class Subscription(models.Model):
    """A repetitive payment."""

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
    payments = models.ManyToManyField("Payment")

    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    profile = models.ForeignKey(
        "PaymentProfile", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        """Return a string representation of the object."""
        return f"Subscription ({self.name})"
