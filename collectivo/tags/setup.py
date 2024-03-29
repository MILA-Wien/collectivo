"""Setup function for the tags extension."""
from django.conf import settings
from django.contrib.auth import get_user_model

from collectivo.extensions.models import Extension

from .apps import TagsConfig
from .models import Tag

User = get_user_model()


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.objects.register(
        name=TagsConfig.name, description=TagsConfig.description, built_in=True
    )

    if settings.COLLECTIVO["example_data"]:
        for i in range(5):
            tag = Tag.objects.get_or_create(name=f"Test tag {i}")[0]
            tag.users.set(list(User.objects.all()))

        tag.description = "This tag has been renamed"
        tag.save()
