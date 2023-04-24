"""URL patterns of the dashboard extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DashboardTileButtonViewSet, DashboardTileViewSet

app_name = "collectivo.dashboard"

router = DefaultRouter()
router.register("tiles", DashboardTileViewSet, basename="tile")
router.register("buttons", DashboardTileButtonViewSet, basename="button")


urlpatterns = [
    path("api/dashboard/", include(router.urls)),
]
