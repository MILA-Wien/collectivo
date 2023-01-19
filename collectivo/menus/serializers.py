"""Serializers of the collectivo user experience module."""
from rest_framework import serializers
from .models import Menu, MenuItem


class MenuCreateSerializer(serializers.ModelSerializer):
    """Serializer to create new menu objects."""

    class Meta:
        """Serializer settings."""

        model = Menu
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    """Serializer for existing menu objects."""

    class Meta:
        """
        Serializer settings.

        The name cannot be changed because it is the primary key to identify
        the object. A new object has to be created to set a new name.
        """

        model = Menu
        fields = '__all__'
        read_only_fields = ('menu_id', )


class MenuItemCreateSerializer(serializers.ModelSerializer):
    """Serializer to create new menu-item objects."""

    class Meta:
        """Serializer settings."""

        model = MenuItem
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for existing menu-item objects."""

    class Meta:
        """
        Serializer settings.

        The name cannot be changed because it is the primary key to identify
        the object. A new object has to be created to set a new name.
        """

        model = MenuItem
        fields = '__all__'
        read_only_fields = ('item_id', )
