"""Views of the user experience module."""
import logging

from rest_framework import generics, viewsets
from rest_framework.response import Response

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

    def update(self, request, *args, **kwargs):
        """Assign individual shift to authenticated user."""
        user_id = self.request.userinfo.user_id
        shift = self.get_object()
        serializer = self.get_serializer(shift, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.assign_user(user_id, shift.id)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """Update individual shift and assign/unassign user."""
        shift = self.get_object()
        assigned_user = self.request.data.get("assigned_user")
        print("view_assigned_user", assigned_user)

        if assigned_user:
            user = models.ShiftUser.objects.get(id=assigned_user)
            print("reached if clause", user.id, user)
            serializer.assign_user(user.id, shift.id)
        else:
            serializer.assign_user(None, shift.id)

        shift.save()
        serializer = self.get_serializer(instance=shift)
        return Response(serializer.data)


class ShiftUserViewSet(viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftUser.objects.all()
    serializer_class = serializers.ShiftUserSerializer
