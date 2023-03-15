"""Setup function for the members extension."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import signals

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
            has_shares=True,
            shares_price=20,
            shares_number_custom=True,
            shares_number_custom_min=9,
            shares_number_standard=9,
            shares_number_social=1,
            has_fees=False,
            has_card=True,
        )
    for name in ["Aktiv", "Investierend"]:
        models.MembershipStatus.objects.get_or_create(
            name=name,
            type=mtype,
        )

    members_extension = Extension.register(
        name=MembersConfig.name.split(".")[-1],
        description=MembersConfig.description,
        version=__version__,
    )

    members_admin_item = MenuItem.register(
        name="members_admin",
        label="Members",
        extension=members_extension,
        required_role_name="members_admin",
        icon_name="pi-users",
        menu_name="main",
    )

    MenuItem.register(
        name="members_table",
        label="Members",
        extension=members_extension,
        component="members",
        icon_name="pi-list",
        parent_item=members_admin_item,
    )

    MenuItem.register(
        name="members_tags",
        label="Tags",
        extension=members_extension,
        component="tags",
        icon_name="pi-tags",
        parent_item=members_admin_item,
    )

    MenuItem.register(
        name="members_profile",
        label="Membership",
        extension=members_extension,
        component="membership",
        icon_name="pi-user",
        required_role_name="members_user",
        menu_name="main",
    )

    DashboardTile.register(
        name="members_registration_tile",
        label="Membership application",
        extension=members_extension,
        component_name="members_registration_tile",
        blocked_role_name="members_user",
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
