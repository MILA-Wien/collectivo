"""Models of the payments extension."""
import datetime

from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords

User = get_user_model()


class PaymentProfile(models.Model):
    """An profile of a user, defining payment methods."""

    user = models.OneToOneField(
        User,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="payment_profile",
        help_text="The user that owns this profile.",
    )

    payment_method = models.CharField(
        choices=[
            ("transfer", "Transfer"),
            ("sepa", "Direct debit"),
        ],
        max_length=30,
    )

    bank_account_iban = models.CharField(max_length=255, null=True, blank=True)
    bank_account_owner = models.CharField(
        max_length=255, null=True, blank=True
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return a string representation of the object."""
        return f"{self.user.first_name} {self.user.last_name}"


class Account(models.Model):
    """An account that can make and receive payments."""

    name = models.CharField(max_length=255)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="account",
        help_text="The user that owns this account.",
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    def __str__(self):
        """Return a string representation of the object."""
        if not self.name and self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.name


class ItemTypeCategory(models.Model):
    """A category of items for accounting."""

    name = models.CharField(max_length=255)
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class ItemType(models.Model):
    """A type of item for accounting."""

    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        "ItemTypeCategory",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return a string representation of the object."""
        if not self.category:
            return self.name
        return f"{self.category} - {self.name}"


class ItemEntry(models.Model):
    """An entry of an item in an invoice."""

    type = models.ForeignKey(
        "ItemType",
        on_delete=models.PROTECT,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The price of the item per unit.",
    )
    amount = models.DecimalField(
        max_digits=10,
        default=1,
        decimal_places=2,
        help_text="The amount of units of the item.",
    )
    invoice = models.ForeignKey(
        "Invoice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="items",
        help_text="The invoice this entry belongs to.",
    )
    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="items",
        help_text="The subscription this entry belongs to.",
    )

    def __str__(self):
        """Return a string representation of the object."""
        return f"{self.type} x {self.amount} @ {self.price}"


class Invoice(models.Model):
    """An invoice."""

    payment_from = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="invoices_out",
        null=True,
    )
    payment_to = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="invoices_in",
        null=True,
    )

    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ("draft", "draft"),
            ("open", "open"),
            ("paid", "paid"),
            ("canceled", "canceled"),
            ("failure", "failure"),
        ],
    )

    date_created = models.DateField(default=datetime.date.today)
    date_due = models.DateField(null=True, blank=True)
    date_paid = models.DateField(null=True, blank=True)

    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoices",
    )

    notes = models.TextField(blank=True)

    history = HistoricalRecords()

    def __str__(self):
        """Return a string representation of the object."""
        return str(self.id)


class Subscription(models.Model):
    """A subscription that creates automatic invoices."""

    payment_from = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="subscriptions_out",
        null=True,
    )
    payment_to = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="subscriptions_in",
        null=True,
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

    date_started = models.DateField(default=datetime.date.today)
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

    notes = models.TextField(blank=True)

    history = HistoricalRecords()

    def __str__(self):
        """Return a string representation of the object."""
        return self.name
