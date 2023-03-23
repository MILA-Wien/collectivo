"""Setup function for the registration_survey extension."""
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.version import __version__

from .apps import SurveyConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=SurveyConfig.name.split(".")[-1],
        description=SurveyConfig.description,
        version=__version__,
    )

    MenuItem.register(
        name="survey_admin",
        label="Surveys",
        extension=extension,
        component="admin",
        icon_name="pi-pencil",
        requires_group="collectivo.core.admin",
        parent="admin",
        order=50,
    )
