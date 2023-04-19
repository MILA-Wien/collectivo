"""Serializers of the dashboard extension."""
from rest_framework import serializers

from .models import DashboardTile, DashboardTileButton


class TileButtonSerializer(serializers.ModelSerializer):
    """Serializer for dashboard tile buttons."""

    class Meta:
        """Serializer settings."""

        model = DashboardTileButton
        fields = "__all__"


class TileSerializer(serializers.ModelSerializer):
    """Serializer for dashboard tiles."""

    class Meta:
        """Serializer settings."""

        model = DashboardTile
        fields = "__all__"
        extra_kwargs = {
            "extension": {"read_only": True},
        }


class TileDisplaySerializer(serializers.ModelSerializer):
    """Serializer to display tiles on the dashboard."""

    buttons = TileButtonSerializer(many=True, read_only=True)
    extension_name = serializers.CharField(
        source="extension.name", read_only=True
    )

    class Meta:
        """Serializer settings."""

        model = DashboardTile
        fields = "__all__"
