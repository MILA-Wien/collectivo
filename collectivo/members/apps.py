"""Configuration file for the members extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from django.contrib.auth import get_user_model
    from mila.registration.models import (
        SurveyGroup,
        SurveyProfile,
        SurveySkill,
    )

    from collectivo.extensions.models import Extension
    from collectivo.memberships.models import (
        Membership,
        MembershipStatus,
        MembershipType,
    )
    from collectivo.payments.models import PaymentProfile
    from collectivo.profiles.models import UserProfile
    from collectivo.tags.models import Tag

    from .models import Member  # , MemberGroup, MemberSkill, MemberTag

    User = get_user_model()

    # Custom migrations

    # Create test member
    # This code is only for testing the migration, now disabled for production
    # The whole app will be removed after migration
    # member = Member.objects.create(
    #     email="test_member_01@example.com",
    #     first_name="MTEST First Name",
    #     last_name="MTEST Last Name",
    #     person_type="legal",
    #     gender="female",
    #     address_street="MTEST Street",
    #     address_number="MTEST Number",
    #     address_stair="MTEST Stair",
    #     address_door="MTEST Door",
    #     address_postcode="MTEST Postcode",
    #     address_city="MTEST City",
    #     address_country="MTEST Country",
    #     phone="MTEST Phone",
    #     birthday="1990-01-01",
    #     occupation="MTEST Occupation",
    #     legal_name="MTEST Legal Name",
    #     legal_type="MTEST Legal Type",
    #     legal_id="MTEST Legal ID",
    #     membership_start="2021-01-01",
    #     membership_type="investing",
    #     shares_number=42,
    #     shares_payment_type="transfer",
    #     bank_account_iban="MTEST IBAN",
    #     bank_account_owner="MTEST Bank Account Owner",
    #     survey_contact="MTEST Survey Contact",
    #     survey_motivation="MTEST Survey Motivation",
    # )
    # member.groups_interested.set(
    #     [MemberGroup.objects.get_or_create(label="Finanzen")[0]]
    # )
    # member.skills.set(
    #     [MemberSkill.objects.get_or_create(label="IT/Digitales")[0]]
    # )
    # member.tags.set(
    #     [
    #         MemberTag.objects.get_or_create(label="Public use approved")[0],
    #         MemberTag.objects.get_or_create(label="MTEST Tag")[0],
    #     ]
    # )

    # Create membership type vor Genossenschaft
    membership_eg = MembershipType.objects.register(
        name="MILA Mitmach-Supermarkt e. G.",
        description="""Mitgliedschaft bei MILA Mitmach-Supermarkt e. G.
        <br>
        <br>Eingetragene Genossenschaft
        <br>Sitz: Wien
        <br>Revisionsverband: Rückenwind
        <br>Firmenbuchnummer FN 598727 g
        <br>Satzung unter <a href="https://www.mila.wien/genossenschaft/">
        mila.wien/genossenschaft</a>
        """,
        has_shares=True,
        shares_amount_per_share=20,
        shares_number_custom=True,
        shares_number_custom_min=9,
        shares_number_standard=9,
        shares_number_social=1,
    )

    # Create membership statuses for Genossenschaft
    active = MembershipStatus.objects.register(name="Aktiv")
    investing = MembershipStatus.objects.register(name="Investierend")
    membership_eg.statuses.set([active, investing])
    membership_eg.save()

    # Create membership type for Verein
    MembershipType.objects.register(
        name="Verein MILA",
        description="Mitgliedschaft bei MILA - Verein zur Stärkung "
        "gesellschaftlicher Solidarität durch die Förderung "
        "einer ökologisch nachhaltigen und sozial gerechten Lebensweise.",
        has_fees=True,
        fees_amount_standard=24,
        fees_amount_social=12,
        fees_amount_custom=True,
        fees_amount_custom_min=24,
        fees_repeat_unit="year",
        fees_repeat_each="1",
    )

    members = Member.objects.all()
    for member in members:
        # Create user
        try:
            user = User.objects.get(username=member.email)
        except User.DoesNotExist:
            user = User.objects.create(username=member.email)
        user.email = member.email
        user.first_name = member.first_name
        user.last_name = member.last_name
        user.save()

        # Create user profile
        profile = UserProfile.objects.get(user=user)
        profile_fields = [
            "person_type",
            "gender",
            "address_street",
            "address_number",
            "address_stair",
            "address_door",
            "address_postcode",
            "address_city",
            "address_country",
            "phone",
            "birthday",
            "occupation",
            "legal_name",
            "legal_type",
            "legal_id",
        ]
        for field in profile_fields:
            if getattr(member, field):
                setattr(profile, field, getattr(member, field))
        profile.save()

        # Create payment profile
        payment_profile = PaymentProfile.objects.get(user=user)
        payment_profile_fields = {
            "payment_method": "shares_payment_type",
            "bank_account_iban": "bank_account_iban",
            "bank_account_owner": "bank_account_owner",
        }
        for paymentfield, memberfield in payment_profile_fields.items():
            if getattr(member, memberfield):
                setattr(
                    payment_profile, paymentfield, getattr(member, memberfield)
                )
        payment_profile.save()

        # Create survey profile
        try:
            survey_profile = SurveyProfile.objects.get(user=user)
        except SurveyProfile.DoesNotExist:
            survey_profile = SurveyProfile.objects.create(user=user)
        survey_profile_fields = [
            "survey_contact",
            "survey_motivation",
        ]
        for field in survey_profile_fields:
            if getattr(member, field):
                setattr(survey_profile, field, getattr(member, field))
        for group in member.groups_interested.all():
            new_group = SurveyGroup.objects.get_or_create(name=group.label)[0]
            survey_profile.groups_interested.add(new_group)
        for skill in member.skills.all():
            new_skill = SurveySkill.objects.get_or_create(name=skill.label)[0]
            survey_profile.skills.add(new_skill)
        survey_profile.save()

        # Get mila_registration extension
        try:
            mila_registration = Extension.objects.get(name="mila_registration")
        except Extension.DoesNotExist:
            mila_registration = Extension.objects.create(
                name="mila_registration"
            )

        # Create tags
        tag_changes = {
            "Statutes approved": "Satzung angenommen",
            "Public use approved": "Öffentliche Verwendung",
        }
        for tag in member.tags.all():
            if tag.label in tag_changes:
                name = tag_changes[tag.label]
            else:
                name = tag.label
            try:
                tag = Tag.objects.get(name=name)
            except Tag.DoesNotExist:
                tag = Tag(name=name)
            tag.save()
            tag.extension = mila_registration
            tag.users.add(user)
            tag.users.add(user)  # Test if error
            tag.save()
            tag.users.add(user)  # Test if error
            tag.save()

        # Create memberships
        try:
            membership = Membership.objects.get(user=user, type=membership_eg)
        except Membership.DoesNotExist:
            membership = Membership(user=user, type=membership_eg)
        membership_fields = {
            "shares_signed": "shares_number",
            "date_started": "membership_start",
            "number": "id",
        }
        for membershipfield, memberfield in membership_fields.items():
            if getattr(member, memberfield):
                setattr(
                    membership, membershipfield, getattr(member, memberfield)
                )
        membership.save()

        # Set membership statuses
        if member.membership_type == "active":
            membership.status = active
        elif member.membership_type == "investing":
            membership.status = investing
        membership.save()


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
