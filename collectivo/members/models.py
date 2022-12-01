"""Models of the members extension."""
from django.db import models


class Member(models.Model):
    """A member of the collective."""

    # Account
    user_id = models.UUIDField(null=True, unique=True)
    email_verified = models.BooleanField(null=True)

    # Membership
    membership_type = models.CharField(
        help_text='Type of membership.',
        max_length=20,
        default='active',
        choices=[
            ('active', 'active'),
            ('investing', 'investing'),
            ('legal', 'legal'),
        ]
    )
    membership_status = models.CharField(
        max_length=20,
        help_text='Current status of membership.',
        default='1_applicant',
        choices=[
            ('1_applicant', '1_applicant'),
            ('2_provisional', '2_provisional'),
            ('3_approved', '3_approved'),
            ('4_normal', '4_normal'),
            ('5_leaving', '5_leaving'),
            ('6_left', '6_left'),
            ('7_deceased', '7_deceased')
        ]
    )

    # Coop shares
    shares_number = models.IntegerField(default=0)
    shares_payment_status = models.CharField(
        max_length=20,
        help_text='Status of payment.',
        default='1_pending',
        choices=[
            ('1_pending', '1_pending'),
            ('2_processing', '2_processing'),
            ('3_success', '3_success'),
            ('4_denied', '4_denied'),
        ]
    )
    shares_payment_type = models.CharField(
        max_length=20,
        help_text='Type of payment.',
        default='sepa',
        choices=[
            ('sepa', 'sepa'),
            # ('transfer', 'transfer')
        ]
    )
    shares_installment_plan = models.BooleanField(default=False)

    # If payment type is not sepa
    # bank_iban
    # bank_blz
    # bank_owner

    # Personal data (real person)
    title_pre = models.CharField(max_length=255, null=True)
    title_post = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # pronouns?
    gender = models.CharField(
        max_length=20,
        null=True,
        choices=[
            ('diverse', 'diverse'),
            ('female', 'female'),
            ('male', 'male'),
        ]
    )
    date_birth = models.DateField(null=True)
    address_street = models.CharField(max_length=255, null=True)
    address_number = models.CharField(max_length=255, null=True)
    address_is_home = models.CharField(
        max_length=20,
        null=True,
        choices=[
            ('Yes', 'Yes'),
            ('No', 'No'),
        ]
    )
    address_co = models.CharField(max_length=255, null=True)
    address_stair = models.CharField(max_length=255, null=True)
    address_door = models.CharField(max_length=255, null=True)
    address_postcode = models.CharField(max_length=255, null=True)
    address_city = models.CharField(max_length=255, null=True)
    address_country = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    phone_2 = models.CharField(max_length=255, null=True)
    email = models.EmailField()  # Snyced with auth!
    email_2 = models.EmailField(null=True)
    homepage = models.CharField(max_length=255, null=True)

    # Personal data (only for active members)
    # Kinder/Miteinkäuferinnen/FamilienID

    # Personal data (only for legal person)
    legal_name = models.CharField(max_length=255, null=True)
    legal_type = models.CharField(max_length=255, null=True)
    legal_seat = models.CharField(max_length=255, null=True)
    legal_type_id = models.CharField(max_length=255, null=True)

    # To be done in serializer (not saved in django, but sent somewhere)
    # Newsletter

    # To be done in frontend (does not have to be saved, just validated)
    # Checkboxen
