"""Manager classes for collectivo."""
from django.db import models


class NameManager(models.Manager):
    """Manager with a register method for models with a name."""

    def register(self, name, *args, **kwargs):
        """Update or create instance based on the attribute "name"."""
        try:
            instance = self.get(name=name)
        except self.model.DoesNotExist:
            instance = self.model(name=name)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
