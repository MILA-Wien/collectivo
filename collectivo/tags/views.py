"""Views of the tags extension."""
import logging

from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import SchemaMixin
from collectivo.utils.permissions import ReadOrIsSuperuser

from . import models, serializers

logger = logging.getLogger(__name__)

User = get_user_model()


class TagViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage tags."""

    permission_classes = [ReadOrIsSuperuser]
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()
    filterset_class = get_filterset(serializers.TagSerializer)
    ordering_fields = get_ordering_fields(serializers.TagSerializer)

    def perform_destroy(self, instance):
        """Prevent deletion if assigned to users."""
        if instance.users.all().exists():
            raise ValidationError(
                "Cannot delete a tag that is assigned to users."
            )
        return super().perform_destroy(instance)
