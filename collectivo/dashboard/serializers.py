"""Serializers of the dashboard extension."""
from rest_framework import serializers

from .models import DashboardTile


class DashboardTileSerializer(serializers.ModelSerializer):
    """Serializer for existing dashboard tiles."""

    extension_name = serializers.CharField(
        source="extension.name", read_only=True
    )

    class Meta:
        """Serializer settings."""

        model = DashboardTile
        fields = "__all__"
