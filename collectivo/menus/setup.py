"""Setup function of the menus extension."""
from collectivo.extensions.models import Extension
from collectivo.menus.apps import MenusConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.objects.register(
        name=MenusConfig.name,
        description=MenusConfig.description,
        built_in=True,
    )
