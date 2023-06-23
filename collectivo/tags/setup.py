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

    extension = Extension.objects.register(
        name=TagsConfig.name, description=TagsConfig.description, built_in=True
    )

    MenuItem.objects.register(
        name="tags_admin",
        label="Tags",
        extension=extension,
        route=extension.name + "/admin",
        icon_name="pi-tags",
        requires_perm=("admin", "core"),
        parent="admin",
        order=2,
    )

    if settings.COLLECTIVO["example_data"]:
        for i in range(5):
            tag = Tag.objects.get_or_create(name=f"Test tag {i}")[0]
            tag.users.set(list(User.objects.all()))
