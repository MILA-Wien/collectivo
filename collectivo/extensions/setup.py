"""Setup function for the users module."""
from collectivo.extensions.models import Extension
from collectivo.extensions.apps import ExtensionsConfig
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.register(
        name=ExtensionsConfig.name,
        description=ExtensionsConfig.description,
        version=__version__,
    )
