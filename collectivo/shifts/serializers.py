"""Serializers of the collectivo user experience module."""
from rest_framework import serializers

from .models import Shift, ShiftAssignment, ShiftProfile


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer for shift."""

    assignments = serializers.SerializerMethodField()
    assigned_users = serializers.SerializerMethodField()

    class Meta:
        """Serializer settings."""

        model = Shift
        fields = "__all__"

    def create(self, validated_data):
        """Create a new shift."""
        shift = Shift.objects.create(**validated_data)
        required_users = validated_data.get("required_users")
        for i in range(required_users):
            ShiftAssignment.objects.create(shift=shift)
        return shift

    def get_assignments(self, obj):
        """Get all assignments for a shift."""
        assignments = ShiftAssignment.objects.filter(shift=obj)
        return AssignmentSerializer(assignments, many=True).data

    def get_assigned_users(self, obj):
        """Get all assigned users for a shift."""
        assignments = ShiftAssignment.objects.filter(shift=obj)
        assigned_users = ShiftProfile.objects.filter(
            shiftassignment__in=assignments
        )
        return ShiftUserSerializer(assigned_users, many=True).data


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for individual shift."""

    class Meta:
        """Serializer settings."""

        model = ShiftAssignment
        fields = "__all__"


class ShiftUserSerializer(serializers.ModelSerializer):
    """Serializer for shift user."""

    class Meta:
        """Serializer settings."""

        model = ShiftProfile
        fields = "__all__"
