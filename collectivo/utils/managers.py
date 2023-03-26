"""Manager classes for collectivo."""
from django.db import models


class NameManager(models.Manager):
    """Manager that allows for registration."""

    def register(self, name, *args, **kwargs):
        """Get or create a based on attribute "name"."""
        try:
            instance = self.get(name=name)
        except self.model.DoesNotExist:
            instance = self.model(name=name)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
