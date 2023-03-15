"""URL patterns of the collectivo core."""
from django.conf import settings
from django.contrib.staticfiles.views import serve
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

app_name = "collectivo"

urlpatterns = []

# Include url patterns from all collectivo extensions
for app in settings.INSTALLED_APPS:
    if app.startswith("collectivo") and app != "collectivo":
        pattern = path("", include(f"{app}.urls"))
        urlpatterns.append(pattern)

# Add debug patterns
if settings.DEVELOPMENT:
    urlpatterns += [
        # Access static files
        re_path(r"^static/(?P<path>.*)$", serve),
        # API Documentation
        path(
            "api/dev/schema/", SpectacularAPIView.as_view(), name="api-schema"
        ),
        path(
            "api/dev/docs/",
            SpectacularSwaggerView.as_view(url_name="collectivo:api-schema"),
            name="api-docs",
        ),
    ]
