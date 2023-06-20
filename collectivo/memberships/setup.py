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

    extension = Extension.register(
        name=apps.ExtensionConfig.name,
        description=apps.ExtensionConfig.description,
        built_in=True,
    )

    # User objects
    MenuItem.register(
        name="memberships_user",
        label="Membership",
        extension=extension,
        route=extension.name + "/profile",
        icon_name="pi-id-card",
        parent="main",
    )

    # Admin objects
    MenuItem.register(
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
    automations = {
        "membership_started": (
            "Send a message to a new member when a membership is created."
        ),
        "membership_accepted": (
            "Send a message to a member when date_accepted of a membership is"
            " set."
        ),
        "membership_cancelled": (
            "Send a message to a member when date_cancelled of a membership is"
            " set."
        ),
        "membership_ended": (
            "Send a message to a member when date_ended of a membership is"
            " set."
        ),
        "membership_shares_paid_increase": (
            "Send a message to a member when shares_paid of a membership is"
            " increased."
        ),
        "membership_shares_paid_decrease": (
            "Send a message to a member when shares_paid of a membership is"
            " decreased."
        ),
        "membership_shares_signed_increase": (
            "Send a message to a member when shares_signed of a membership is"
            " increased."
        ),
        "membership_shares_signed_decrease": (
            "Send a message to a member when shares_signed of a membership is"
            " decreased."
        ),
    }
    for key, description in automations.items():
        EmailAutomation.objects.register(
            name=key,
            description=description,
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
            enable_registration=True,
        )
        mst2 = models.MembershipType.objects.register(
            name="Test Membership Type 1 (Fees)",
            description="""This is a type of membership that where members have
             to pay monthly fees.
            <p style="font-weight: bold">This is a bold paragraph.</p>""",
            has_fees=True,
            fees_amount_standard=100,
        )
        types = [mst1, mst2]

        # Create membership statuses
        statuses = []
        for sname in ["Test Status 1", "Test Status 2"]:
            status = models.MembershipStatus.objects.register(name=sname)
            statuses.append(status)
        status_cycle = cycle(statuses)

        # Create memberships
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
