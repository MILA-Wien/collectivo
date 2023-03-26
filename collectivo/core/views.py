"""Views of the core extension."""
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import HistoryMixin, SchemaMixin
from collectivo.utils.permissions import IsSuperuser
from collectivo.version import __version__

from . import serializers

User = get_user_model()
Group = User.groups.field.related_model


class AboutView(APIView):
    """API view for information about the collectivo instance."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse()})
    def get(self, request):
        """Return information about the collectivo instance."""
        data = {
            "version": __version__,
        }
        return Response(data)


class UserViewSet(SchemaMixin, HistoryMixin, viewsets.ModelViewSet):
    """Viewset for django users."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsSuperuser]
    filterset_class = get_filterset(serializers.UserSerializer)
    ordering_fields = get_ordering_fields(serializers.UserSerializer)


class GroupViewSet(SchemaMixin, HistoryMixin, viewsets.ModelViewSet):
    """Viewset for django groups."""

    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [IsSuperuser]
    filterset_class = get_filterset(serializers.GroupSerializer)
    ordering_fields = get_ordering_fields(serializers.GroupSerializer)
