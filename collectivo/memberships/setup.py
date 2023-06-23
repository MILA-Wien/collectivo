"""Setup function for the memberships extension."""
from itertools import cycle
from logging import getLogger

from django.conf import settings
from django.contrib.auth import get_user_model

from collectivo.emails.models import EmailAutomation
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.utils.dev import DEV_MEMBERS

from . import apps, models

logger = getLogger(__name__)


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.objects.register(
        name=apps.ExtensionConfig.name,
        description=apps.ExtensionConfig.description,
        built_in=True,
    )

    # User objects
    MenuItem.objects.register(
        name="memberships_user",
        label="Membership",
        extension=extension,
        route=extension.name + "/profile",
        icon_name="pi-id-card",
        parent="main",
    )

    # Admin objects
    MenuItem.objects.register(
        name="memberships_admin",
        label="Memberships",
        extension=extension,
        route=extension.name + "/admin",
        requires_perm=("admin", "core"),
        icon_name="pi-id-card",
        parent="admin",
        order=10,
    )

    # Email automations
    automations = [f"Membership {stage}" for stage in models.MEMBERSHIP_STAGES]
    automations += [
        "Paid shares increased",
        "Paid shares decreased",
        "Signed shares increased",
        "Signed shares decreased",
    ]
    for automation in automations:
        EmailAutomation.objects.register(
            name=automation,
            description=(
                "Membership data can be accessed via {{ membership }}."
            ),
            extension=extension,
            admin_only=False,
        )

    if settings.COLLECTIVO["example_data"] is True:
        # Create membership types

        mst1 = models.MembershipType.objects.register(
            name="Test Membership Type 1 (Shares)",
            description=(
                "This is a type of membership where members can hold shares."
            ),
            has_shares=True,
            shares_amount_per_share=100,
            shares_number_custom=True,
            shares_number_custom_min=1,
        )
        mst2 = models.MembershipType.objects.register(
            name="Test Membership Type 1 (Fees)",
            description="""This is a type of membership that where members have
             to pay monthly fees.""",
            has_fees=True,
            fees_amount_standard=100,
        )
        mst3 = models.MembershipType.objects.register(
            name="Test Membership Type 3 (Shares)",
            description="""This is a type of membership where members can hold
             shares, open for registration.""",
            has_shares=True,
            shares_amount_per_share=100,
            shares_number_custom=True,
            shares_number_custom_min=1,
            enable_registration=True,
        )
        types = [mst1, mst2, mst3]

        # Create membership statuses
        statuses = []
        for sname in ["Test Status 1", "Test Status 2"]:
            status = models.MembershipStatus.objects.register(name=sname)
            statuses.append(status)
        for ty in types:
            ty.statuses.set(statuses)
        status_cycle = cycle(statuses)

        # Create memberships
        types = [mst1, mst2]
        for first_name in DEV_MEMBERS:
            if first_name == "user_not_member":
                continue
            email = f"test_{first_name}@example.com"
            user = get_user_model().objects.get(email=email)
            for type in types:
                try:
                    m = models.Membership.objects.get_or_create(
                        user=user,
                        type=type,
                    )[0]
                    m.status = next(status_cycle)
                    m.shares_signed = 10
                    m.save()
                except models.Membership.MultipleObjectsReturned:
                    logger.warning("Error creating example memberships.")
