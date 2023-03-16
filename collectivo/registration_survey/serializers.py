"""Serializers of the registration survey extension."""

from rest_framework import serializers

from . import models


class SurveyProfileSerializer(serializers.ModelSerializer):
    """Serializer for registration surveys."""

    class Meta:
        """Serializer settings."""

        model = models.SurveyProfile
        fields = "__all__"


class SurveyGroupSerializer(serializers.ModelSerializer):
    """Serializer for registration survey groups."""

    class Meta:
        """Serializer settings."""

        model = models.SurveyGroup
        fields = "__all__"


class SurveySkillSerializer(serializers.ModelSerializer):
    """Serializer for registration survey skills."""

    class Meta:
        """Serializer settings."""

        model = models.SurveySkill
        fields = "__all__"
