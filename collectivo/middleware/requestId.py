"""Middleware to add a unique request_id to the request."""
import uuid


class AddRequestId():
    """Middleware to add a unique request_id to the request."""

    def __init__(self, get_response):
        """Initiate middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Add a unique request_id to the request."""
        request.META["X-Request-ID"] = str(uuid.uuid4())
        response = self.get_response(request)
        response["X-Request-ID"] = request.META["X-Request-ID"]
        return response
