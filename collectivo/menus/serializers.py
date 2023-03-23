"""Serializers of the collectivo user experience module."""
from django.db.models import Q
from rest_framework import serializers

from .models import Menu, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for menu items."""

    class Meta:
        """Serializer settings."""

        model = MenuItem
        fields = "__all__"
        depth = 3


class MenuSerializer(serializers.ModelSerializer):
    """Serializer for menus."""

    items = serializers.SerializerMethodField()
    unique_name = serializers.SerializerMethodField()

    class Meta:
        """Serializer settings."""

        model = Menu
        fields = "__all__"
        depth = 3

    def get_unique_name(self, instance: Menu):
        """Return the unique name of the menu."""
        return instance.extension.name + "." + instance.name

    def get_items(self, instance: Menu):
        """Return the items of the menu.

        Items are filtered based on required group and sorted based on order.
        """

        items = instance.items.all().order_by("order")

        request = self.context.get("request", None)
        if request:
            items = items.filter(
                Q(requires_group__isnull=True)
                | Q(requires_group__in=request.user.groups.all())
            )

        return MenuItemSerializer(items, many=True).data
