"""Utility functions of the collectivo package."""
import importlib

from django.conf import settings
from django.db.models import Model


def get_instance(cls: Model, value: str | Model) -> Model:
    """Get an instance of a model based on a string with the instance name."""
    if isinstance(value, str):
        return cls.objects.get_or_create(name=value)[0]
    return value


def get_object_from_settings(setting_name):
    """Return a default model as defined in the settings."""
    cls = settings.COLLECTIVO[setting_name]
    module_name, class_name = cls.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
