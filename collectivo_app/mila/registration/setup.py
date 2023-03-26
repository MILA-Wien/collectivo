"""Setup function for the registration_survey extension."""
from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.memberships.models import MembershipStatus, MembershipType
from collectivo.version import __version__

from .apps import SurveyConfig
from .models import SurveyGroup, SurveySkill


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=SurveyConfig.name.split(".")[-1],
        description=SurveyConfig.description,
        version=__version__,
    )

    DashboardTile.register(
        name="mila_membership_tile",
        label="Membership",
        extension=extension,
        component="mila_membership_tile",
    )

    for tname in ["Genossenschaft MILA", "Verein MILA"]:
        MembershipType.objects.register(name=tname)

    # Create membership statuses
    for sname in ["Aktiv", "Investierend"]:
        MembershipStatus.objects.register(name=sname)

    # Create survey skills
    for sname in [
        "Immobilien/Architektur/Planung",
        "Einzelhandel",
        "Handwerk (Elektrik, Tischlerei, …)",
        "Genossenschaft/Partizipation/Organisationsentwicklung",
        "Kommunikation (Medien, Grafik, Text,…)",
        "IT/Digitales",
        "Finanzen (BWL, Buchhaltung,…)",
    ]:
        SurveySkill.objects.register(name=sname)

    # Create survey groups
    for gname in [
        "Infogespräche",
        "Sortiment",
        "Öffentlichkeitsarbeit",
        "Finanzen",
        "Genossenschaft",
        "IT und Digitales",
        "Events",
        "Standort",
        "Minimarkt",
    ]:
        SurveyGroup.objects.register(name=gname)
