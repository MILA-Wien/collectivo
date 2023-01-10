"""Serializers of the emails module."""
from rest_framework import serializers
from . import models


class EmailDesignSerializer(serializers.ModelSerializer):
    """Serializer for email designs."""

    class Meta:
        """Serializer settings."""

        model = models.EmailDesign
        fields = '__all__'


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
        fields = '__all__'
        read_only_fields = ('status', 'status_message', 'created')
