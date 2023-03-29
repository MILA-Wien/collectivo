"""Setup function for the tags extension."""
from django.conf import settings

from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.version import __version__

from .apps import TagsConfig
from .models import Tag


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=TagsConfig.name, description=TagsConfig.description, built_in=True
    )

    MenuItem.register(
        name="tags_admin",
        label="Tags",
        extension=extension,
        component="admin",
        icon_name="pi-tags",
        requires_group="collectivo.core.admin",
        parent="admin",
        order=2,
    )

    if settings.COLLECTIVO["dev.create_test_data"]:
        for i in range(100):
            Tag.objects.get_or_create(name=f"Test tag {i}")
