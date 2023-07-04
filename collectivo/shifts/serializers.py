"""Serializers of the collectivo user experience module."""
from rest_framework import serializers

from collectivo.utils.schema import Schema

from .models import Shift, ShiftProfile, ShiftSlot


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer for shift."""

    next_occurence = serializers.SerializerMethodField()

    def get_next_occurence(self, obj):
        """Get the next occurence of the shift."""
        return obj.get_next_occurence()

    class Meta:
        """Serializer settings."""

        model = Shift
        fields = "__all__"
        schema: Schema = {
            "structure": [
                {
                    "fields": [
                        "name",
                        "description",
                    ],
                    "style": "col",
                },
                {
                    "fields": ["required_users", "shift_points", "repeat"],
                },
                {
                    "fields": [
                        "repeat_start",
                        "repeat_end",
                        "abcd_week",
                        "abcd_day",
                        "starting_time",
                        "ending_time",
                    ],
                    "visible": {
                        "condition": "equals",
                        "value": "abcd",
                        "field": "repeat",
                    },
                },
                {
                    "fields": ["date", "starting_time", "ending_time"],
                    "visible": {
                        "condition": "equals",
                        "value": "none",
                        "field": "repeat",
                    },
                },
                {
                    "fields": ["notes"],
                },
            ]
        }


class ShiftOccurenceSerializer(serializers.Serializer):
    """Serializer for shift occurence."""

    date = serializers.DateField()
    shift = ShiftSerializer()


class ShiftOpenShiftsSerializer(ShiftSerializer):
    """Serializer for open shifts."""

    class Meta:
        """Serializer settings."""

        model = Shift
        fields = "__all__"


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for individual shift."""

    class Meta:
        """Serializer settings."""

        model = ShiftSlot
        fields = "__all__"


class ShiftUserSerializer(serializers.ModelSerializer):
    """Serializer for shift user."""

    class Meta:
        """Serializer settings."""

        model = ShiftProfile
        fields = "__all__"
