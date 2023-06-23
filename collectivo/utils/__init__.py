"""Utility functions of the collectivo package."""
import importlib

from django.conf import settings
from django.db.models import Model


def get_instance(
    cls: Model, value: str | tuple | Model, needs_ext=False
) -> Model:
    """Get an instance of a model based on a string with the instance name."""
    if isinstance(value, str):
        if needs_ext:
            raise ValueError("No extension is given.")
        return cls.objects.get_or_create(name=value)[0]
    elif isinstance(value, tuple):
        from collectivo.extensions.models import Extension

        name, ext = value
        ext = get_instance(Extension, ext)
        return cls.objects.get_or_create(name=name, extension=ext)[0]
    return value


def get_object_from_settings(setting_name):
    """Return a default model as defined in the settings."""
    cls = settings.COLLECTIVO[setting_name]
    module_name, class_name = cls.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
