"""Views of the registration survey extension."""
from rest_framework import viewsets

from collectivo.core.permissions import HasGroup
from collectivo.utils.schema import SchemaMixin

from . import models, serializers


class SurveyProfileViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage registration surveys."""

    permission_classes = [HasGroup]
    required_groups = ["collectivo.registration_survey.admin"]
    serializer_class = serializers.SurveyProfileSerializer
    queryset = models.SurveyProfile.objects.all()


class SurveyGroupViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage registration survey groups."""

    permission_classes = [HasGroup]
    required_groups = ["collectivo.registration_survey.admin"]
    serializer_class = serializers.SurveyGroupSerializer
    queryset = models.SurveyGroup.objects.all()


class SurveySkillViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage registration survey skills."""

    permission_classes = [HasGroup]
    required_groups = ["collectivo.registration_survey.admin"]
    serializer_class = serializers.SurveySkillSerializer
    queryset = models.SurveySkill.objects.all()
