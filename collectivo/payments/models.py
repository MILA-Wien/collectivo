"""Models of the payments extension."""
from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords


class PaymentProfile(models.Model):
    """An account that can make and receive payments."""

    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="payment_profile",
        help_text="The user that owns this profile.",
    )

    # TODO: Use user id as default
    accounting_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="A key to identify this entity in the accounting system.",
    )

    # Payment details
    payment_method = models.CharField(
        choices=[
            ("transfer", "transfer"),
            ("sepa", "sepa"),
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
        return str(self.user)


class ItemType(models.Model):
    """A type of item for accounting."""

    name = models.CharField(max_length=50)
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


class Item(models.Model):
    """An item for accounting."""

    name = models.CharField(max_length=50)
    type = models.ForeignKey(
        "ItemType",
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
        if self.category:
            return f"{self.category.name} - {self.name}"
        return f"{self.name}"


class ItemEntry(models.Model):
    """An entry of an item in an invoice."""

    item = models.ForeignKey(
        "Item",
        on_delete=models.PROTECT,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The price of the item per unit.",
    )
    amount = models.DecimalField(
        max_digits=10,
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
        return self.type


class Invoice(models.Model):
    """An invoice for a transaction."""

    name = models.CharField(max_length=50)

    payment_from = models.ForeignKey(
        "PaymentProfile", on_delete=models.PROTECT, related_name="invoices_out"
    )
    payment_to = models.ForeignKey(
        "PaymentProfile", on_delete=models.PROTECT, related_name="invoices_in"
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
            ("pending", "pending"),
            ("canceled", "canceled"),
            ("failed", "failed"),
            ("paid", "paid"),
        ],
    )

    date_due = models.DateField(null=True)
    date_paid = models.DateField(null=True)

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
        return self.name


class Subscription(models.Model):
    """A subscription that creates automatic invoices."""

    name = models.CharField(max_length=50)

    payment_from = models.ForeignKey(
        "PaymentProfile",
        on_delete=models.PROTECT,
        related_name="subscriptions_out",
    )
    payment_to = models.ForeignKey(
        "PaymentProfile",
        on_delete=models.PROTECT,
        related_name="subscriptions_in",
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

    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)

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


class Payment(models.Model):
    """A transaction of money."""

    paid = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_from = models.ForeignKey(
        "PaymentProfile", on_delete=models.PROTECT, related_name="payments_out"
    )
    payment_to = models.ForeignKey(
        "PaymentProfile", on_delete=models.PROTECT, related_name="payments_in"
    )
    invoice = models.ForeignKey(
        "Invoice",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
    )
    notes = models.TextField(blank=True)

    history = HistoricalRecords()
