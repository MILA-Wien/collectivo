"""Setup function for the memberships extension."""
from itertools import cycle

from django.conf import settings
from django.contrib.auth import get_user_model

from collectivo.core.setup import TEST_MEMBERS
from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.version import __version__

from . import apps, models


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=apps.ExtensionConfig.name.split(".")[-1],
        description=apps.ExtensionConfig.description,
        version=__version__,
    )

    # User objects
    MenuItem.register(
        name="memberships_user",
        label="Membership",
        extension=extension,
        component="user",
        icon_name="pi-id-card",
        parent="main",
    )

    DashboardTile.register(
        name="members_registration_tile",
        label="Membership",
        extension=extension,
        component="members_registration_tile",
    )

    # Admin objects
    MenuItem.register(
        name="memberships_admin",
        label="Memberships",
        extension=extension,
        component="admin",
        requires_group="collectivo.core.admin",
        icon_name="pi-id-card",
        parent="admin",
        order=10,
    )

    if settings.COLLECTIVO["dev.create_test_data"] is True:
        # Create membership types
        types = []
        for tname in ["MILA Genossenschaft", "MILA Verein"]:
            type = models.MembershipType.objects.get_or_create(name=tname)[0]
            types.append(type)

        # Create membership statuses
        statuses = []
        for sname in ["Aktiv", "Investierend"]:
            status = models.MembershipStatus.objects.register(name=sname)
            statuses.append(status)
        status_cycle = cycle(statuses)

        # Create memberships
        for first_name in TEST_MEMBERS:
            if first_name == "user_not_member":
                continue
            email = f"test_{first_name}@example.com"
            user = get_user_model().objects.get(email=email)
            for type in types:
                models.Membership.objects.get_or_create(
                    user=user, type=type, status=next(status_cycle)
                )
