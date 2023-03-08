"""Models of the members extension."""
from django.db import models


class MemberTag(models.Model):
    """A tag that can be assigned to members."""

    label = models.CharField(max_length=255, unique=True)
    built_in = models.BooleanField(default=False, editable=False)

    def __str__(self):
        """Return string representation."""
        return self.label


class MemberGroup(models.Model):
    """A group that can be assigned to members."""

    label = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """Return string representation."""
        return self.label


class MemberSkill(models.Model):
    """A skill that can be assigned to members."""

    label = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """Return string representation."""
        return self.label


class MembershipSubtype(models.Model):
    """A sub type of membership. E.g. active or passive member."""

    label = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """Return string representation."""
        return self.label


class MemberCard(models.Model):
    """A membership card that can be assigned to members."""

    date_created = models.DateField()
    active = models.BooleanField(default=False)


# TODO: MAKE THIS INTO A GENERIC MEMBERSHIP??


class CoMemberType(models.Model):
    """A type of co-member that can be assigned to a membership type."""

    label = models.CharField(max_length=255, unique=True)
    max_members = models.IntegerField(null=True, blank=True)
    has_card = models.BooleanField(default=False)


class CoMembers(models.Model):
    """A co-member that can be assigned to a membership."""

    type = models.ForeignKey("CoMembershipType", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    birth_date = models.DateField(null=True)

    # Optional depending on CoMemberType
    card = models.ForeignKey(
        "MemberCard", null=True, blank=True, on_delete=models.SET_NULL
    )


class MembershipType(models.Model):
    """A type of membership. E.g. in a specific organisation."""

    label = models.CharField(max_length=255, unique=True)
    subtypes = models.ManyToManyField("MembershipSubType", blank=True)
    comemberships = models.ManyToManyField("CoMembershipType", blank=True)

    has_shares = models.BooleanField(default=False)
    shares_price = models.DecimalField()

    has_fees = models.BooleanField(default=False)
    fees_custom = models.BooleanField(default=False)
    fees_price = models.DecimalField(null=True, blank=True)  # If not custom
    fees_price_min = models.DecimalField(null=True, blank=True)  # If custom

    has_card = models.BooleanField(default=False)

    def __str__(self):
        """Return string representation."""
        return self.label


class Membership(models.Model):
    """A membership of a member."""

    started = models.DateField(null=True, blank=True)
    cancelled = models.DateField(null=True, blank=True)
    ended = models.DateField(null=True, blank=True)
    type = models.ForeignKey("MembershipType", on_delete=models.CASCADE)
    subtype = models.ForeignKey("MembershipSubtype", on_delete=models.CASCADE)

    # Optional depending on membership type
    shares = models.IntegerField(null=True, blank=True)
    fees = models.DecimalField(null=True, blank=True)
    comembers = models.ManyToManyField("MemberAddon", blank=True)
    card = models.ForeignKey(
        "MemberCard", null=True, blank=True, on_delete=models.SET_NULL
    )

    # Connection to payments module
    payments = models.ManyToManyField("payments.Payment", blank=True)


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

    # Survey data
    # TODO: Move to separate model
    survey_contact = models.TextField(null=True, blank=True)
    survey_motivation = models.TextField(null=True, blank=True)
    groups_interested = models.ManyToManyField(
        "MemberGroup", related_name="groups_interested", blank=True
    )
    skills = models.ManyToManyField("MemberSkill", blank=True)

    # Other
    tags = models.ManyToManyField("MemberTag", blank=True)
    # TODO remove related name after survey data is moved
    groups = models.ManyToManyField(
        "MemberGroup", related_name="groups", blank=True
    )
    admin_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        """Return string representation."""
        return f"{self.first_name} {self.last_name} ({self.id})"
