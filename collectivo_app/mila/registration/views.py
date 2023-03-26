"""Views of the registration survey extension."""
from rest_framework import mixins, viewsets

from collectivo.core.permissions import IsAuthenticated, IsSuperuser
from collectivo.profiles.models import UserProfile
from collectivo.utils.mixins import HistoryMixin, SchemaMixin

from . import models, serializers


class SurveyProfileViewSet(HistoryMixin, SchemaMixin, viewsets.ModelViewSet):
    """Manage registration surveys."""

    permission_classes = [IsSuperuser]
    serializer_class = serializers.SurveyProfileSerializer
    queryset = models.SurveyProfile.objects.all()


class SurveyGroupViewSet(HistoryMixin, SchemaMixin, viewsets.ModelViewSet):
    """Manage registration survey groups."""

    permission_classes = [IsSuperuser]
    serializer_class = serializers.SurveyGroupSerializer
    queryset = models.SurveyGroup.objects.all()


class SurveySkillViewSet(HistoryMixin, SchemaMixin, viewsets.ModelViewSet):
    """Manage registration survey skills."""

    permission_classes = [IsSuperuser]
    serializer_class = serializers.SurveySkillSerializer
    queryset = models.SurveySkill.objects.all()


class MilaRegisterViewSet(
    SchemaMixin, viewsets.GenericViewSet, mixins.CreateModelMixin
):
    """Endpoint for MILA users to register as coop members."""

    queryset = UserProfile.objects.all()
    serializer_class = serializers.MemberRegisterSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Create member with authenticated user."""
        extra_fields = {
            "user": self.request.user,
        }
        if "tags" in serializer.validated_data:
            extra_fields["tags"] = serializer.validated_data["tags"]
        serializer.save(**extra_fields)
