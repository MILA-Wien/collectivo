"""Views of the user experience module."""
import logging

from rest_framework import viewsets

from . import models, serializers

logger = logging.getLogger(__name__)


class ShiftViewSet(viewsets.ModelViewSet):
    """Manage shiftss."""

    queryset = models.Shift.objects.all()
    serializers_class = serializers.ShiftSerializer
