"""Views of the core extension."""

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from collectivo.users.permissions import IsAuthenticated
from collectivo.version import __version__
