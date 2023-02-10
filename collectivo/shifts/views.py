"""Views of the user experience module."""

from rest_framework import viewsets

from . import models, serializers


class GeneralShiftViewSet(viewsets.ModelViewSet):
    """Manage general shifts."""

    queryset = models.GeneralShift.objects.all()
    serializer_class = serializers.GeneralShiftSerializer
    filterset_fields = {
        "shift_title": ["exact"],
        "first_shift_date": ["gte", "lte", "exact", "gt", "lt"],
        "shift_type": ["exact"],
        "shift_week": ["exact"],
        "starting_date_time": ["gte", "lte", "exact", "gt", "lt"],
        "duration": ["exact"],
        "end_date_time": ["gte", "lte", "exact", "gt", "lt"],
        "required_users": ["exact"],
        "shift_day": ["exact"],
        "additional_info_general": ["exact"],
    }


class IndividualShiftViewSet(viewsets.ModelViewSet):
    """Manage individual shifts."""

    queryset = models.IndividualShift.objects.all()
    serializer_class = serializers.IndividualShiftSerializer


class ShiftUserViewSet(viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftUser.objects.all()
    serializer_class = serializers.ShiftUserSerializer
