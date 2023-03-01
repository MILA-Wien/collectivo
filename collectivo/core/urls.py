"""URL patterns of the core extension."""
from django.urls import path

from . import views

app_name = "collectivo.core"

urlpatterns = [
    # Core API views
    path("api/core/about/", views.AboutView.as_view(), name="version"),
]
