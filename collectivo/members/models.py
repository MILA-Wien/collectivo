"""Models of the members extension."""
from django.db import models, transaction
from django.db.models import signals
from simple_history.models import HistoricalRecords

from collectivo.extensions.models import Extension
from collectivo.payments.models import Payment

# --------------------------------------------------------------------------- #
# Membership types ---------------------------------------------------------- #
# --------------------------------------------------------------------------- #


class MembershipType(models.Model):
    """A type of membership. E.g. for a specific organisation."""

    name = models.CharField(max_length=255, unique=True)

    has_shares = models.BooleanField(default=False)
    shares_amount_per_share = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )
    shares_number_custom = models.BooleanField(default=False)
    shares_number_custom_min = models.IntegerField(null=True, blank=True)
    shares_number_custom_max = models.IntegerField(null=True, blank=True)
    shares_number_standard = models.IntegerField(null=True, blank=True)
    shares_number_social = models.IntegerField(null=True, blank=True)

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

    has_card = models.BooleanField(default=False)

    comembership_of = models.ForeignKey(
        "MembershipType", null=True, blank=True, on_delete=models.CASCADE
    )
    comembership_max = models.IntegerField(null=True, blank=True)

    email_new_membership = models.ForeignKey(
        "emails.EmailTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return string representation."""
        return self.name


class MembershipStatus(models.Model):
    """A status that members can have within a membership of a certain type.

    E.g. active or passive membership within a specific organisation.
    """

    name = models.CharField(max_length=255, unique=True)
    type = models.ForeignKey("MembershipType", on_delete=models.CASCADE)

    history = HistoricalRecords()

    def __str__(self):
        """Return string representation."""
        return self.name


# --------------------------------------------------------------------------- #
# Memberships --------------------------------------------------------------- #
# --------------------------------------------------------------------------- #


class MembershipManager(models.Manager):
    """Manager for membership models."""

    def create(self, *args, **kwargs):
        """Create a membership with automatic number."""
        highest = self.filter(type=kwargs["type"]).order_by("number").last()
        if highest is None:
            number = 1
        else:
            number = highest.number + 1

        membership = super().create(*args, number=number, **kwargs)
        # TODO: Test & Activate this feature
        # self.send_welcome_mail(membership)
        return membership

    def send_welcome_mail(self, membership):
        """Send welcome mail to new member if specified."""

        if membership.type.welcome_mail is not None:
            from collectivo.emails.models import EmailCampaign

            campaign = EmailCampaign.objects.create(
                recipients=[membership.member.user],
                template=membership.type.welcome_mail,
                extension=Extension.objects.get(name="members"),
            )
            campaign.send()


class Membership(models.Model):
    """A membership of a member."""

    objects = MembershipManager()

    member = models.ForeignKey(
        "Member", on_delete=models.CASCADE, related_name="memberships"
    )
    number = models.IntegerField(unique=True)

    started = models.DateField(null=True, blank=True)
    cancelled = models.DateField(null=True, blank=True)
    ended = models.DateField(null=True, blank=True)
    type = models.ForeignKey("MembershipType", on_delete=models.CASCADE)
    status = models.ForeignKey(
        "MembershipStatus", null=True, blank=True, on_delete=models.CASCADE
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

    # Connection to payment module
    shares_payments = models.ManyToManyField(
        "payments.Payment", related_name="membership_shares"
    )
    fees_subscription = models.ForeignKey(
        "payments.Subscription",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="membership_fees",
    )

    history = HistoricalRecords()

    def create_payment_for_shares(self):
        """Create payment for shares."""
        old = Membership.objects.get(pk=self.pk) if self.pk else None
        old_shares_signed = old.shares_signed if old else 0

        if self.type.has_shares:
            shares_diff = self.shares_signed - old_shares_signed

            if shares_diff < 0:
                raise NotImplementedError("Cannot remove shares")

            if shares_diff > 0:
                payment = Payment.objects.create(
                    name="Shares",
                    description=f"{shares_diff} shares for {self.type.name}",
                    user=self.member.user.payments,
                    amount=shares_diff * self.type.shares_amount_per_share,
                )
                return payment

    def save(self, *args, **kwargs):
        """Save membership and create payments."""
        with transaction.atomic():
            payment = self.create_payment_for_shares()
            super().save(*args, **kwargs)
            if payment is not None:
                self.shares_payments.add(payment)
                super().save()


class MembershipCard(models.Model):
    """A membership card that can be assigned to members."""

    date_created = models.DateField()
    active = models.BooleanField(default=False)
    membership = models.ForeignKey(
        "Membership", on_delete=models.CASCADE, null=True, blank=True
    )

    history = HistoricalRecords()


def update_membership_from_payment(sender, instance, **kwargs):
    """Update membership from payment."""

    # Only update if payment has been changed to successfull
    if instance.status != "success":
        return
    if instance.pk:
        old = Payment.objects.get(pk=instance.pk)
        if old.status == "success":
            return

    # Write paid shares to membership
    if instance.membership_shares.exists():
        membership = instance.membership_shares.first()
        shares_paid = int(
            instance.amount / membership.type.shares_amount_per_share
        )
        membership.shares_paid += shares_paid
        membership.save()


signals.pre_save.connect(
    update_membership_from_payment,
    sender=Payment,
    dispatch_uid="update_membership_from_payment",
    weak=False,
)


# --------------------------------------------------------------------------- #
# Members (which can have multiple memberships) ----------------------------- #
# --------------------------------------------------------------------------- #


class Member(models.Model):
    """A member of the collective."""

    # Account
    user = models.OneToOneField(
        "auth.User", primary_key=True, on_delete=models.CASCADE
    )

    # Personal data
    person_type = models.CharField(
        help_text="Type of person.",
        max_length=20,
        default="natural",
        choices=[
            ("natural", "natural"),
            ("legal", "legal"),
        ],
    )
    gender = models.CharField(
        max_length=20,
        default="diverse",
        choices=[
            ("diverse", "diverse"),
            ("female", "female"),
            ("male", "male"),
        ],
    )
    address_street = models.CharField(max_length=255)
    address_number = models.CharField(max_length=255)
    address_stair = models.CharField(max_length=255, null=True, blank=True)
    address_door = models.CharField(max_length=255, null=True, blank=True)
    address_postcode = models.CharField(max_length=255)
    address_city = models.CharField(max_length=255)
    address_country = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True)

    # Personal data (only for natural people)
    birthday = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)

    # Personal data (only for legal person)
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    legal_type = models.CharField(max_length=255, null=True, blank=True)
    legal_id = models.CharField(max_length=255, null=True, blank=True)

    # Admin data
    notes = models.TextField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        """Return string representation."""
        return f"{self.user.first_name} {self.user.last_name}"
