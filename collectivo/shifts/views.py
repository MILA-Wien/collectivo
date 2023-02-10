"""Views of the user experience module."""
import logging

from rest_framework import viewsets

from . import models, serializers

logger = logging.getLogger(__name__)


class GeneralShiftViewSet(viewsets.ModelViewSet):
    """Manage general shifts."""

    queryset = models.GeneralShift.objects.all()
    serializer_class = serializers.GeneralShiftSerializer


class IndividualShiftViewSet(viewsets.ModelViewSet):
    """Manage individual shifts."""

    queryset = models.IndividualShift.objects.all()
    serializer_class = serializers.IndividualShiftSerializer


class ShiftUserViewSet(viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftUser.objects.all()
    serializer_class = serializers.ShiftUserSerializer
