"""Setup function for the members extension."""
from django.conf import settings

from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.members.apps import MembersConfig
from collectivo.members.models import MemberGroup, MemberSkill, MemberTag
from collectivo.menus.models import MenuItem
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

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

    if settings.DEVELOPMENT:
        tags = ["Statutes approved", "Public use approved", "Founding event"]
        for label in tags:
            MemberTag.objects.get_or_create(label=label)
        groups = [
            "Infogespräche",
            "Sortiment",
            "Öffentlichkeitsarbeit",
            "Finanzen",
            "Genossenschaft",
            "IT und Digitales",
            "Events",
            "Standort",
            "Minimarkt",
        ]
        for label in groups:
            MemberGroup.objects.get_or_create(label=label)
        skills = [
            "Immobilien/Architektur/Planung",
            "Einzelhandel",
            "Handwerk (Elektrik, Tischlerei, …)",
            "Genossenschaft/Partizipation/Organisationsentwicklung",
            "Kommunikation (Medien, Grafik, Text,…)",
            "IT/Digitales",
            "Finanzen (BWL, Buchhaltung,…)",
        ]
        for label in skills:
            MemberSkill.objects.get_or_create(label=label)
