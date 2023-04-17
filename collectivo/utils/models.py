"""Utilities for collectivo models."""

from django import forms

from collectivo.utils.exceptions import ImproperlyConfigured


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


class SingleInstance:
    """Mixin for models that should only have one instance."""

    @classmethod
    def object(cls, check_valid=False):
        """Get or create instance."""
        if not cls.objects.exists():
            obj = cls.objects.create()
        else:
            obj = cls.objects.first()
        if check_valid and not obj.is_valid():
            raise ImproperlyConfigured(f"{cls.__name__} is not valid.")

    def is_valid(self):
        """Check if object is valid."""

        class Form(forms.ModelForm):
            """Form to check if object is valid."""

            class Meta:
                """Meta class."""

                model = self.__class__
                fields = "__all__"

        return Form(instance=self).is_valid()

    def save(self, *args, **kwargs):
        """Save object or raise exception if an instance already exists."""
        if self.pk is None and self.__class__.objects.exists():
            raise Exception("Only one instance of this model allowed.")
        super().save(*args, **kwargs)
