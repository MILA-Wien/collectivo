"""URL Configuration of collectivo_app."""
import logging
import re

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

logger = logging.getLogger(__name__)

urlpatterns = [
    path("admin/", admin.site.urls),
    # TODO: This serves all media files with public access. Should be improved.
    re_path(
        r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")),
        serve,
        kwargs={"document_root": settings.MEDIA_ROOT},
    ),
]

# Extensions
for app in settings.COLLECTIVO["extensions"]:
    try:
        pattern = path("", include(f"{app}.urls"))
        urlpatterns.append(pattern)
    except ModuleNotFoundError:
        pass  # If there is no urls.py, continue without error
    except Exception as e:
        logger.error(f"Error reading urls.py for {app}: {e}", exc_info=True)

# API Documentation
if settings.COLLECTIVO["api_docs"]:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="api-schema"),
            name="api-docs",
        ),
    ]

handler400 = "rest_framework.exceptions.bad_request"
handler500 = "rest_framework.exceptions.server_error"
