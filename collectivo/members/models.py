"""Models of the members extension."""
from django.db import models

# --------------------------------------------------------------------------- #
# Membership types ---------------------------------------------------------- #
# --------------------------------------------------------------------------- #


class MembershipType(models.Model):
    """A type of membership. E.g. in a specific organisation."""

    label = models.CharField(max_length=255, unique=True)

    has_shares = models.BooleanField(default=False)
    shares_price = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )
    shares_number_custom = models.BooleanField(default=False)
    shares_number_custom_min = models.IntegerField(null=True, blank=True)
    shares_number_standard = models.IntegerField(null=True, blank=True)
    shares_number_social = models.IntegerField(null=True, blank=True)

    has_fees = models.BooleanField(default=False)
    fees_custom = models.BooleanField(default=False)
    fees_repeat_unit = models.CharField(
        max_length=20,
        default="year",
        choices=[
            ("year", "year"),
            ("month", "month"),
        ],
    )
    fees_repeat_each = models.IntegerField(default=1)
    fees_custom_min = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )
    fees_standard = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )
    fees_social = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )

    has_card = models.BooleanField(default=False)

    comembership_of = models.ForeignKey(
        "MembershipType", null=True, blank=True, on_delete=models.CASCADE
    )
    comembership_max = models.IntegerField(null=True, blank=True)

    welcome_mail = models.ForeignKey(
        "emails.EmailTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        """Return string representation."""
        return self.label


class MembershipStatus(models.Model):
    """A status that members can have within a membership of a certain type.

    E.g. active or passive member."""

    label = models.CharField(max_length=255, unique=True)
    type = models.ForeignKey("MembershipType", on_delete=models.CASCADE)

    def __str__(self):
        """Return string representation."""
        return self.label


# --------------------------------------------------------------------------- #
# Memberships --------------------------------------------------------------- #
# --------------------------------------------------------------------------- #


class MembershipManager(models.Manager):
    def create(self, *args, **kwargs):
        """Create a membership with automatic number."""
        highest = self.filter(type=kwargs["type"]).order_by("number").last()
        if highest is None:
            number = 1
        else:
            number = highest.number + 1
        return super().create(*args, number=number, **kwargs)


class Membership(models.Model):
    """A membership of a member."""

    objects = MembershipManager()

    member = models.ForeignKey(
        "Member", on_delete=models.CASCADE, related_name="memberships"
    )
    number = models.IntegerField(unique=True)
    active = models.BooleanField(default=False)
    started = models.DateField(null=True, blank=True)
    cancelled = models.DateField(null=True, blank=True)
    ended = models.DateField(null=True, blank=True)
    type = models.ForeignKey("MembershipType", on_delete=models.CASCADE)
    status = models.ForeignKey(
        "MembershipStatus", null=True, blank=True, on_delete=models.CASCADE
    )

    # Optional depending on membership type
    shares = models.IntegerField(null=True, blank=True)
    fees = models.DecimalField(
        max_digits=100, decimal_places=2, null=True, blank=True
    )
    comembership_of = models.ForeignKey(
        "Membership", blank=True, null=True, on_delete=models.CASCADE
    )

    # TODO: Connection to payments module
    # payments = models.ManyToManyField("payments.Payment", blank=True)


class MembershipCard(models.Model):
    """A membership card that can be assigned to members."""

    date_created = models.DateField()
    active = models.BooleanField(default=False)
    membership = models.ForeignKey(
        "Membership", on_delete=models.CASCADE, null=True, blank=True
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
    address_street = models.CharField(max_length=255, null=True, blank=True)
    address_number = models.CharField(max_length=255, null=True, blank=True)
    address_stair = models.CharField(max_length=255, null=True, blank=True)
    address_door = models.CharField(max_length=255, null=True, blank=True)
    address_postcode = models.CharField(max_length=255, null=True, blank=True)
    address_city = models.CharField(max_length=255, null=True, blank=True)
    address_country = models.CharField(max_length=255, null=True, blank=True)
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

    def __str__(self):
        """Return string representation."""
        return f"{self.first_name} {self.last_name}"
