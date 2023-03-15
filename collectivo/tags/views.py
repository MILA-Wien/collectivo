"""Views of the members extension."""
import logging

from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from collectivo.core.permissions import ReadOrIsSuperuser
from collectivo.utils.schema import SchemaMixin

from . import models, serializers

logger = logging.getLogger(__name__)

User = get_user_model()


class TagViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage tags."""

    permission_classes = [ReadOrIsSuperuser]
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()

    def perform_destroy(self, instance):
        """Prevent deletion if assigned to users."""
        if instance.users.all().exists():
            raise ValidationError(
                "Cannot delete a tag that is assigned to users."
            )
        return super().perform_destroy(instance)