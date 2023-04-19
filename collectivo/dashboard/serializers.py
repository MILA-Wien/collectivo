"""Serializers of the dashboard extension."""
from django.template import Context, Template
from rest_framework import serializers
from rest_framework.exceptions import ParseError

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
    content = serializers.SerializerMethodField()

    class Meta:
        """Serializer settings."""

        model = DashboardTile
        fields = "__all__"

    def get_content(self, obj):
        """Get the content of the tile."""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            content = Template(obj.content).render(
                Context({"user": request.user})
            )
            return content
        raise ParseError("No user in context of TileDisplaySerializer.")
