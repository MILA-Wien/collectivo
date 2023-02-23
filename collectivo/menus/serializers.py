"""Serializers of the collectivo user experience module."""
from rest_framework import serializers

from .models import Menu, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for existing menu-item objects."""

    class Meta:
        """Serializer settings."""

        model = MenuItem
        fields = "__all__"
        depth = 3


class MenuSerializer(serializers.ModelSerializer):
    """Serializer for existing menu objects."""

    items = serializers.SerializerMethodField()

    class Meta:
        """Serializer settings."""

        model = Menu
        fields = "__all__"
        depth = 3

    def get_items(self, instance: Menu):
        songs = instance.items.all().order_by("order")
        return MenuItemSerializer(songs, many=True).data
