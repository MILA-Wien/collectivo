"""Middleware to log `*/api/*` requests and responses."""
import socket
import time
import logging


request_logger = logging.getLogger(__name__)


class RequestLogMiddleware:
    """Request Logging Middleware."""

    def __init__(self, get_response):
        """Initiate middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Handle calls."""
        start_time = time.time()
        log_data = {
            "remote_address": request.META["REMOTE_ADDR"],
            "server_hostname": socket.gethostname(),
            "request_method": request.method,
            "request_path": request.get_full_path(),
        }

        # Request passes on to controller
        response = self.get_response(request)

        if hasattr(response, 'status_code'):
            log_data["status_code"] = response.status_code
            if str(response.status_code)[0] in '45':
                log_data["response_body"] = response.content
        if hasattr(request, 'userinfo') and \
                hasattr(request.userinfo, 'user_id'):
            log_data["user_id"] = request.userinfo.user_id

        if request.META.get("X-Request-ID") is not None:
            log_data["request_id"] = request.META["X-Request-ID"]

        # add runtime to our log_data
        log_data["run_time"] = time.time() - start_time
        msg = '\n'+'\n'.join([f'  {k}: {v}' for k, v in log_data.items()])
        request_logger.info(msg=msg)

        return response

    def process_exception(self, request, exception):
        """Log unhandled exceptions as well."""
        try:
            raise exception
        except Exception as e:
            request_logger.exception("Unhandled Exception: " + str(e))
