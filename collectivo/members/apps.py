"""Configuration file for the members extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from django.contrib.auth import get_user_model
    from mila.registration.models import SurveyProfile

    from collectivo.memberships.models import (
        Membership,
        MembershipStatus,
        MembershipType,
    )
    from collectivo.payments.models import PaymentProfile
    from collectivo.profiles.models import UserProfile

    from .models import Member

    User = get_user_model()

    # Custom migrations

    # Create membership types

    # mst1 = MembershipType.objects.register(
    #     name="Test Membership Type 1 (Shares)",
    #     description="This is a type of membership that where members can"
    #     " hold shares.",
    #     has_shares=True,
    #     shares_amount_per_share=100,
    #     shares_number_custom=True,
    #     shares_number_custom_min=1,
    # )
    # mst2 = MembershipType.objects.register(
    #     name="Test Membership Type 1 (Fees)",
    #     description="This is a type of membership that where members have"
    #     " to pay monthly fees.",
    #     has_fees=True,
    #     fees_amount_standard=100,
    # )
    # types = [mst1, mst2]

    # # Create membership statuses
    # statuses = []
    # for sname in ["Test Status 1", "Test Status 2"]:
    #     status = MembershipStatus.objects.register(name=sname)
    #     statuses.append(status)
    # status_cycle = cycle(statuses)

    # members = Member.objects.all()
    # for member in members:
    #     # Create user
    #     try:
    #         user = User.objects.get(username=member.email)
    #     except User.DoesNotExist:
    #         user = User.objects.create(username=member.email)
    #     user.email = member.email
    #     user.first_name = member.first_name
    #     user.last_name = member.last_name
    #     user.save()

    #     # Create user profile
    #     profile = UserProfile.objects.get(user=user)
    #     profile_fields = [
    #         "person_type",
    #         "gender",
    #         "address_street",
    #         "address_number",
    #         "address_stair",
    #         "address_door",
    #         "address_postcode",
    #         "address_city",
    #         "address_country",
    #         "phone",
    #         "birthday",
    #         "occupation",
    #         "legal_name",
    #         "legal_type",
    #         "legal_id",
    #     ]
    #     for field in profile_fields:
    #         if getattr(member, field):
    #             setattr(profile, field, getattr(member, field))
    #     profile.save()

    #     # Create payment profile
    #     payment_profile = PaymentProfile.objects.get(user=user)
    #     payment_profile_fields = {
    #         "payment_method": "shares_payment_type",
    #         "bank_account_iban": "bank_account_iban",
    #         "bank_accuont_owner": "bank_accuont_owner",
    #     }
    #     for paymentfield, memberfield in payment_profile_fields.items():
    #         if getattr(member, memberfield):
    #             setattr(payment_profile, paymentfield, getattr(member, memberfield))

    #     # Create memberships
    #     try:
    #         membership = Membership.objects.get(user=user)
    #     except Membership.DoesNotExist:
    #         membership = Membership(user=user)


class MembersConfig(AppConfig):
    """Configuration class for the members extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.members"

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)
