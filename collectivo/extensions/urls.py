"""URL patterns of the extensions module."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.extensions"

router = DefaultRouter()
router.register("extensions", views.ExtensionViewSet)

urlpatterns = [path("api/extensions/", include(router.urls))]
