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
        name=MembersConfig.name,
        description=MembersConfig.description,
        version=__version__,
    )

    MenuItem.register(
        name="members",
        label="Members",
        extension=members_extension,
        component_name="members",
        required_role_name="members_user",
        menu_name="admin",
    )

    for name, label, required_role in [
        ("members", "Members", "members_admin"),
        ("tags", "Tags", "members_admin"),
        ("profile", "Membership", "members_user"),
    ]:
        MenuItem.register(
            name=name,
            label=label,
            extension=members_extension,
            component_name=name,
            required_role_name=required_role,
            menu_name="admin",
        )

    DashboardTile.register(
        name="members_registration_tile",
        label="Membership application",
        extension=members_extension,
        component_name="members_registration_tile",
        blocked_role="members_user",
    )

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
