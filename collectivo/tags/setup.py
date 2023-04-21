"""Setup function for the tags extension."""
from django.conf import settings
from django.contrib.auth import get_user_model

from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem

from .apps import TagsConfig
from .models import Tag

User = get_user_model()


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
        for i in range(5):
            tag = Tag.objects.get_or_create(name=f"Test tag {i}")[0]
            tag.users.set(list(User.objects.all()))
