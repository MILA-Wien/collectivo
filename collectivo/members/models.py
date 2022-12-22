"""Models of the members extension."""
from django.db import models


class MemberTag(models.Model):
    """A tag that can be assigned to members."""

    label = models.CharField(max_length=255, unique=True)

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


class MemberStatus(models.Model):
    """A status that can be assigned to members."""

    label = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """Return string representation."""
        return self.label


class MemberCard(models.Model):
    """A membership card that can be assigned to members."""

    date_created = models.DateField()
    active = models.BooleanField(default=False)


class MemberAddon(models.Model):
    """A person that can be assigned to members."""

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(null=True)
    person_type = models.CharField(
        max_length=20,
        choices=[
            ('child', 'child'),
            ('coshopper', 'coshopper'),
        ]
    )
    birth_date = models.DateField(null=True)
    membership_card = models.ForeignKey(
        'MemberCard', null=True, on_delete=models.SET_NULL)


class Member(models.Model):
    """A member of the collective."""

    # Account
    user_id = models.UUIDField(null=True, unique=True)
    email = models.EmailField(null=True)
    email_verified = models.BooleanField(null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    # Personal data
    person_type = models.CharField(
        help_text='Type of person.',
        max_length=20,
        default='natural',
        choices=[
            ('natural', 'natural'),
            ('legal', 'legal'),
        ]
    )
    gender = models.CharField(
        max_length=20,
        default='diverse',
        choices=[
            ('diverse', 'diverse'),
            ('female', 'female'),
            ('male', 'male'),
        ]
    )
    address_street = models.CharField(max_length=255, null=True)
    address_number = models.CharField(max_length=255, null=True)
    address_stair = models.CharField(max_length=255, null=True)
    address_door = models.CharField(max_length=255, null=True)
    address_postcode = models.CharField(max_length=255, null=True)
    address_city = models.CharField(max_length=255, null=True)
    address_country = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)

    # Personal data (only for active members)
    children = models.ManyToManyField(
        'MemberAddon', related_name="children", blank=True)
    coshopper = models.ForeignKey(
        'MemberAddon', related_name="coshoppers",
        null=True, on_delete=models.SET_NULL)

    # Personal data (only for natural people)
    birthday = models.DateField(null=True)
    occupation = models.CharField(max_length=255, null=True)

    # Personal data (only for legal person)
    legal_name = models.CharField(max_length=255, null=True)
    legal_type = models.CharField(max_length=255, null=True)
    legal_id = models.CharField(max_length=255, null=True)

    # Membership
    membership_start = models.DateField(null=True)
    membership_cancelled = models.DateField(null=True)
    membership_end = models.DateField(null=True)
    membership_type = models.CharField(
        max_length=20,
        choices=[
            ('active', 'active'),
            ('investing', 'investing'),
        ]
    )
    membership_status = models.ForeignKey(
        'MemberStatus', null=True, on_delete=models.SET_NULL)
    membership_card = models.ForeignKey(
        'MemberCard', null=True, on_delete=models.SET_NULL)

    # Membership - Coop shares
    shares_number = models.IntegerField(null=True)
    shares_payment_date = models.DateField(null=True)
    shares_payment_type = models.CharField(
        max_length=20, null=True,
        help_text='Type of payment.',
        choices=[
            ('sepa', 'sepa'),
            ('transfer', 'transfer')
        ]
    )
    bank_account_iban = models.CharField(max_length=255, null=True)
    bank_account_owner = models.CharField(max_length=255, null=True)

    # Survey data
    survey_contact = models.TextField(null=True)
    survey_motivation = models.TextField(null=True)
    groups_interested = models.ManyToManyField(
        'MemberGroup', related_name="groups_interested", blank=True)
    skills = models.ManyToManyField('MemberSkill', blank=True)

    # Other
    tags = models.ManyToManyField('MemberTag', blank=True)
    groups = models.ManyToManyField(
        'MemberGroup', related_name="groups", blank=True)
    admin_notes = models.TextField(null=True)
