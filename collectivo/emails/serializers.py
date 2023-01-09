"""Serializers of the emails module."""
from rest_framework import serializers
from . import models


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for email templates."""

    class Meta:
        """Serializer settings."""

        model = models.EmailTemplate
        fields = '__all__'


class EmailBatchSerializer(serializers.ModelSerializer):
    """Serializer for email logs."""

    class Meta:
        """Serializer settings."""

        model = models.EmailBatch
        exclude = ['status']
