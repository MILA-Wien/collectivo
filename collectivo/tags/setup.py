"""Setup function for the tags extension."""
from django.conf import settings

from collectivo.extensions.models import Extension
from collectivo.version import __version__

from .apps import TagsConfig
from .models import Tag


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.register(
        name=TagsConfig.name.split(".")[-1],
        description=TagsConfig.description,
        version=__version__,
    )

    if settings.CREATE_TEST_DATA:
        for i in range(100):
            Tag.objects.get_or_create(name=f"Test tag {i}")
