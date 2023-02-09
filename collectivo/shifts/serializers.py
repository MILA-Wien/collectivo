"""Serializers of the collectivo user experience module."""
from rest_framework import serializers

from .models import GeneralShift, IndividualShift, ShiftUser


class GeneralShiftSerializer(serializers.ModelSerializer):
    """Serializer for general shift."""

    # individual_shifts = IndividualShiftSerializer(many=True)

    class Meta:
        """Serializer settings."""

        model = GeneralShift
        fields = "__all__"

    def create(self, validated_data):
        """Create a new general shift."""
        general_shift = GeneralShift.objects.create(**validated_data)
        required_users = validated_data.get("required_users")
        for i in range(required_users):
            IndividualShift.objects.create(general_shift=general_shift)

        return general_shift


class IndividualShiftSerializer(serializers.ModelSerializer):
    """Serializer for individual shift."""

    class Meta:
        """Serializer settings."""

        model = IndividualShift
        fields = "__all__"

    def assign_user(self, user_id, individual_shift_id):
        """Assign user to individual shift."""
        print("hitting assign_user", user_id, individual_shift_id)
        if user_id is None:
            user = None
        else:
            user = ShiftUser.objects.get(id=user_id)
        individual_shift = IndividualShift.objects.get(id=individual_shift_id)
        print("correct assignment?", user, individual_shift, individual_shift.id)
        # if-clause to check if shift is already assigned
        if individual_shift.assigned_user is None:
            individual_shift.assigned_user = user
            individual_shift.save()
            print("reached if clause in asssign_user", individual_shift.assigned_user)
        # elif-clause to unassign shift from user
        elif user is None:
            individual_shift.assigned_user = None
            individual_shift.save()
        else:
            raise serializers.ValidationError("Shift already assigned")


class ShiftUserSerializer(serializers.ModelSerializer):
    """Serializer for shift user."""

    class Meta:
        """Serializer settings."""

        model = ShiftUser
        fields = "__all__"
