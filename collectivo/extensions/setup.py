"""Setup function for the extensions module."""
from collectivo.extensions.apps import ExtensionsConfig
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=ExtensionsConfig.name,
        description=ExtensionsConfig.description,
        built_in=True,
    )

    MenuItem.register(
        name="extensions",
        label="Extensions",
        extension=extension,
        parent="admin",
        route=extension.name + "/admin",
        requires_perm="superuser",
        icon_name="pi-box",
        order=90,
    )
