"""Views of the devtools app."""
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response


class TestAPIView(APIView):
    """An API view of the test_extension app."""

    def get(self, request):
        """Return success message."""
        data = {
            'message': 'Hi! I am the test_extension.',
        }
        return Response(data)


def test_html_view(request):
    """An HTML view of the test_extension app."""
    return render(request, "test_extension/test_page.html")
