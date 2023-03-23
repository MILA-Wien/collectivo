"""Setup function for the members extension."""
from itertools import cycle

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import signals

from collectivo.core.setup import TEST_USERS
from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.members.apps import MembersConfig
from collectivo.menus.models import MenuItem
from collectivo.version import __version__

from . import models


def add_user_to_members_user_group(sender, instance, created, **kwargs):
    """Add a user to the collectivo.members.user group."""
    if created:
        instance.groups.add(Group.objects.get(name="collectivo.members.user"))
        instance.save()


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Group.objects.get_or_create(name="collectivo.members.user")

    try:
        mtype = models.MembershipType.objects.get(name="Genossenschaft MILA")
    except models.MembershipType.DoesNotExist:
        mtype = models.MembershipType.objects.create(
            name="Genossenschaft MILA",
            has_card=True,
            has_shares=True,
            shares_amount_per_share=20,
            shares_number_custom=True,
            shares_number_custom_min=9,
            shares_number_standard=9,
            shares_number_social=1,
        )
    # for sname in ["Aktiv", "Investierend"]:
    #     models.MembershipStatus.objects.get_or_create_by_name(name=sname)

    members_extension = Extension.register(
        name=MembersConfig.name.split(".")[-1],
        description=MembersConfig.description,
        version=__version__,
    )

    MenuItem.register(
        name="members_table",
        label="Members",
        extension=members_extension,
        component="admin",
        requires_group="collectivo.core.admin",
        icon_name="pi-users",
        parent="admin",
        order=0,
    )

    MenuItem.register(
        name="members_profile",
        label="Membership",
        extension=members_extension,
        component="profile",
        icon_name="pi-user",
        required_role_name="members_user",
        parent="main",
    )

    DashboardTile.register(
        name="members_registration_tile",
        label="Membership",
        extension=members_extension,
        component="members_registration_tile",
    )

    for item in MenuItem.objects.filter(extension=members_extension):
        if item.name not in [
            "members_admin",
            "members_table",
            "members_tags",
            "members_profile",
        ]:
            item.delete()

    # Signals
    signals.post_save.connect(
        add_user_to_members_user_group,
        sender=get_user_model(),
        dispatch_uid="add_user_to_members_user_group",
        weak=False,
    )

    if settings.CREATE_TEST_DATA is True:
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
        for first_name in TEST_USERS:
            if first_name == "user_not_member":
                continue
            email = f"test_{first_name}@example.com"
            profile = models.MemberProfile.objects.get_or_create(
                user=get_user_model().objects.get(email=email),
            )[0]
            for type in types:
                models.Membership.objects.get_or_create(
                    profile=profile, type=type, status=next(status_cycle)
                )
