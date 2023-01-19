"""Serializers of the dashboard extension."""
from rest_framework import serializers
from .models import DashboardTile


class DashboardTileCreateSerializer(serializers.ModelSerializer):
    """Serializer for new dashboard tiles."""

    class Meta:
        """Serializer settings."""

        model = DashboardTile
        fields = '__all__'


class DashboardTileSerializer(serializers.ModelSerializer):
    """Serializer for existing dashboard tiles."""

    class Meta:
        """
        Serializer settings.

        The name cannot be changed because it is the primary key to identify
        the object. A new object has to be created to set a new name.
        """

        model = DashboardTile
        fields = '__all__'
        read_only_fields = ('tile_id', )
