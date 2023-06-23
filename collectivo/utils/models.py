"""Utilities for collectivo models."""

from rest_framework import serializers


class SingleInstance:
    """Mixin for models that should only have one instance."""

    @classmethod
    def object(cls, check_valid=False):
        """Get or create instance."""
        if not cls.objects.exists():
            obj = cls.objects.create()
        else:
            obj = cls.objects.first()
        if check_valid:
            obj.is_valid()
        return obj

    def is_valid(self):
        """Check if object is valid."""

        class TempSerializer(serializers.ModelSerializer):
            """Serializer to check if object is valid."""

            class Meta:
                """Meta class."""

                model = self.__class__
                fields = "__all__"

        temp_serializer = TempSerializer(data=TempSerializer(self).data)
        temp_serializer.is_valid(raise_exception=True)

    def save(self, *args, **kwargs):
        """Save object or raise exception if an instance already exists."""
        if self.pk is None and self.__class__.objects.exists():
            raise Exception("Only one instance of this model allowed.")
        super().save(*args, **kwargs)
