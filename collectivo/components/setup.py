"""Setup function for the components module."""

from collectivo.extensions.apps import ExtensionsConfig
from collectivo.extensions.models import Extension


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.objects.register(
        name=ExtensionsConfig.name,
        description=ExtensionsConfig.description,
        built_in=True,
    )
