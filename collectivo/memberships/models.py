"""Models of the memberships extension."""
from datetime import date

from django.contrib.auth import get_user_model
from django.db import models, transaction
from simple_history.models import HistoricalRecords

from collectivo.core.models import Permission, PermissionGroup
from collectivo.dashboard.models import DashboardTile, DashboardTileButton
from collectivo.extensions.models import Extension
from collectivo.utils.exceptions import ExtensionNotInstalled
from collectivo.utils.managers import NameManager

try:
    from collectivo.payments.models import (
        Invoice,
        ItemEntry,
        ItemType,
        ItemTypeCategory,
        Subscription,
    )

    payments_installed = True
except ImportError:
    payments_installed = False


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

    enable_registration = models.BooleanField(
        default=False,
        verbose_name="Enable registration",
        help_text="Whether users can register for this membership type.",
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return string representation."""
        return self.name

    def save(self, *args, **kwargs):
        """Save the model and set up registration."""
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.create_group()
            if self.enable_registration:
                self.create_registration_form()
            else:
                self.delete_registration_form()

    def delete(self, *args, **kwargs):
        """Delete the model and remove registration."""
        self.delete_group()
        self.delete_registration_form()
        super().delete(*args, **kwargs)

    def create_group(self, remove=False):
        """Handle the group for this membership type."""
        extension = Extension.objects.get(name="memberships")
        permission = Permission.objects.register(
            name=self.name,
            extension=extension,
        )
        group = PermissionGroup.objects.register(
            name=self.name,
            description=(
                "Members of this group have a membership of the type '{}'."
                .format(self.name)
            ),
            extension=extension,
            users_custom=False,
            perms_custom=True,
        )
        group.permissions.add(permission)
        group.save()

    def delete_group(self):
        """Delete the group for this membership type."""
        extension = Extension.objects.get(name="memberships")
        try:
            Permission.objects.get(
                name=self.name, extension=extension
            ).delete()
        except Permission.DoesNotExist:
            pass

        try:
            PermissionGroup.objects.get(
                name=self.name, extension=extension
            ).delete()
        except PermissionGroup.DoesNotExist:
            pass

    def create_registration_form(self):
        """Create a registration form for this membership type."""

        extension = Extension.objects.get(name="memberships")

        permission = Permission.objects.get(
            name=self.name, extension=extension
        )

        tile = DashboardTile.objects.register(
            name=self.name,
            label="Membership application",
            extension=extension,
            source="db",
            content="Click here to register as a member of {}.".format(
                self.name
            ),
            requires_not_perm=permission,
        )

        button = DashboardTileButton.objects.register(
            name=self.name,
            label="Register",
            extension=Extension.objects.get(name="memberships"),
            link_type="internal",
            link="memberships/register/{}/1".format(self.id),
        )

        tile.buttons.add(button)

    def delete_registration_form(self):
        """Delete the registration form for this membership type."""
        extension = Extension.objects.get(name="memberships")

        try:
            DashboardTile.objects.get(
                name=self.name, extension=extension
            ).delete()
        except DashboardTile.DoesNotExist:
            pass

        try:
            DashboardTileButton.objects.get(
                name=self.name, extension=extension
            ).delete()
        except DashboardTileButton.DoesNotExist:
            pass


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

MEMBERSHIP_STAGES = ["applied", "accepted", "resigned", "excluded", "ended"]


class Membership(models.Model):
    """A membership of a user."""

    class Meta:
        """Meta settings."""

        unique_together = [("number", "type"), ("user", "type")]

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    number = models.IntegerField(verbose_name="Membership number")

    date_applied = models.DateField(null=True, blank=True, default=date.today)
    date_accepted = models.DateField(null=True, blank=True)
    date_resigned = models.DateField(null=True, blank=True)
    date_excluded = models.DateField(null=True, blank=True)
    date_ended = models.DateField(null=True, blank=True)

    type = models.ForeignKey(
        "MembershipType", on_delete=models.PROTECT, related_name="memberships"
    )
    status = models.ForeignKey(
        "MembershipStatus", null=True, blank=True, on_delete=models.PROTECT
    )
    stage = models.CharField(
        max_length=20,
        choices=[(x, x) for x in MEMBERSHIP_STAGES],
        default="applied",
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

    def save_basic(self, *args, **kwargs):
        """Save membership and generate membership number."""
        if self.number is None:
            self.number = self.generate_membership_number()

        super().save()

    def save(self, *args, **kwargs):
        """Save membership and create payments."""
        self.create_invoices()
        self.assign_group()

        # Store data before saving
        old = Membership.objects.filter(pk=self.pk)
        old_data = {field.name: None for field in self._meta.fields}
        is_new = False if old.exists() else True
        if not is_new:
            for field in self._meta.fields:
                old_data[field] = getattr(old.first(), field.name)

        # Create or update object
        self.save_basic()

        self.send_emails(is_new, old_data)

    def send_emails(self, new, data):
        """Send automatic emails."""

        # Trigger automation if membership stage has changed
        if data["stage"] != self.stage:
            self.send_email(f"Membership {self.stage}")

        # Trigger automation for changes in shares
        if (self.shares_paid or 0) > (data["shares_paid"] or 0):
            self.send_email("Paid shares increased")
        elif (self.shares_paid or 0) < (data["shares_paid"] or 0):
            self.send_email("Paid shares decreased")
        if (self.shares_paid or 0) > (data["shares_signed"] or 0):
            self.send_email("Signed shares increased")
        elif (self.shares_signed or 0) < (data["shares_signed"] or 0):
            self.send_email("Signed shares decreased")

    def delete(self, *args, **kwargs):
        """Delete the model and remove registration."""
        self.assign_group(remove=True)
        super().delete(*args, **kwargs)

    def __str__(self):
        """Return string representation."""
        return (
            f"{self.user.first_name} {self.user.last_name} ({self.type.name})"
        )

    def assign_group(self, remove=False):
        """Assign the user to the group of the membership type."""
        extension = Extension.objects.get(name="memberships")
        group = PermissionGroup.objects.get(
            name=self.type.name,
            extension=extension,
        )
        if remove:
            group.users.remove(self.user)
        else:
            group.users.add(self.user)
        group.save()

    def send_email(self, trigger):
        """Send automatic email."""
        self.type.refresh_from_db()
        from collectivo.emails.models import EmailAutomation
        from collectivo.extensions.models import Extension

        extension = Extension.objects.get(name="memberships")

        automation = EmailAutomation.objects.get(
            name=trigger, extension=extension
        )
        automation.send([self.user], context={"membership": self})

    def update_shares_paid(self):
        """Update the number of shares paid for this membership.

        This method depends to the collectivo.payments extension.
        """

        if not payments_installed:
            raise ExtensionNotInstalled("collectivo.payments")

        extension = Extension.objects.get(name="memberships")
        item_category = ItemTypeCategory.objects.get_or_create(
            name="Shares", extension=extension
        )[0]
        item_type = ItemType.objects.get_or_create(
            name=self.type.name,
            category=item_category,
            extension=extension,
        )[0]
        entries = ItemEntry.objects.filter(
            type=item_type,
            invoice__payment_from=self.user.account,
            invoice__status="paid",
        )
        if entries.exists():
            shares_paid = (
                sum([entry.amount * entry.price for entry in entries])
                / self.type.shares_amount_per_share
            )

            self.shares_paid = shares_paid
            self.save_basic()

    def create_invoices(self):
        """Create invoices for this membership.

        This method depends to the collectivo.payments extension.
        """

        if not payments_installed:
            raise ExtensionNotInstalled("collectivo.payments")

        # Create invoices for shares
        if self.type.has_shares:
            extension = Extension.objects.get(name="memberships")
            item_category = ItemTypeCategory.objects.get_or_create(
                name="Shares", extension=extension
            )[0]
            item_type = ItemType.objects.get_or_create(
                name=self.type.name,
                category=item_category,
                extension=extension,
            )[0]
            entries = ItemEntry.objects.filter(
                type=item_type,
                invoice__payment_from=self.user.account,
            )

            # Get current status
            invoiced = sum([entry.amount * entry.price for entry in entries])
            to_pay = self.type.shares_amount_per_share * self.shares_signed

            # Create invoice if needed
            if invoiced < to_pay:
                invoice = Invoice.objects.create(
                    payment_from=self.user.account,
                    status="open",
                )
                price = self.type.shares_amount_per_share
                ItemEntry.objects.create(
                    invoice=invoice,
                    type=item_type,
                    amount=(to_pay - invoiced) / price,
                    price=price,
                )

        # Create subscriptions for fees
        if self.type.has_fees:
            extension = Extension.objects.get(name="memberships")
            item_category = ItemTypeCategory.objects.get_or_create(
                name="Fees", extension=extension
            )[0]
            item_type = ItemType.objects.get_or_create(
                name=self.type.name,
                category=item_category,
                extension=extension,
            )[0]
            entries = ItemEntry.objects.filter(
                type=item_type,
                subscription__status="active",
                subscription__payment_from=self.user.account,
            )

            # Create or update subscription
            if entries.exists():
                entry = entries.first()
                subscription = entry.subscription

                subscription.status = "active"
                subscription.repeat_each = self.type.fees_repeat_each
                subscription.repeat_unit = self.type.fees_repeat_unit
                subscription.save()

                entry.amount = 1
                entry.price = self.fees_amount
                entry.save()

            else:
                subscription = Subscription.objects.create(
                    payment_from=self.user.account,
                    status="active",
                    extension=extension,
                    date_started=self.date_applied,
                    repeat_each=self.type.fees_repeat_each,
                    repeat_unit=self.type.fees_repeat_unit,
                )
                price = self.fees_amount
                ItemEntry.objects.create(
                    subscription=subscription,
                    type=item_type,
                    amount=1,
                    price=self.fees_amount,
                )
