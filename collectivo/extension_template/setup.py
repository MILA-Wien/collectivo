"""Setup function of the extension_template extension."""
from collectivo.extensions.models import Extension

from .apps import ExtensionConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    name = ExtensionConfig.name.split(".")[-1]  # Remove collectivo. prefix
    Extension.register(
        name=name, description=ExtensionConfig.description, built_in=True
    )
