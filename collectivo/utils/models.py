"""Utilities for collectivo models."""


class RegisterMixin:
    """Mixin to add the register method to models."""

    @classmethod
    def register(cls, name, **kwargs):
        """Register an object by name.

        This is similar to get_or_create,
        only that it uses only the keyword name to get the object,
        but also updates an existing instance if it has changed.
        """

        try:
            instance = cls.objects.get(name=name)
        except cls.DoesNotExist:
            instance = cls(name=name)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()

        return instance
