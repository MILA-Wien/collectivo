"""URL patterns of the core extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from collectivo.utils.routers import DirectDetailRouter

from . import views

app_name = "collectivo.core"

router = DefaultRouter()
router.register("users", views.UserViewSet)
router.register(
    "users-extended", views.UserProfilesViewSet, basename="users-extended"
)

router.register("permission", views.PermissionViewSet, basename="permissions")
router.register("groups", views.PermissionGroupViewSet, basename="groups")

router_dd = DirectDetailRouter()
router_dd.register("settings", views.CoreSettingsViewSet, basename="settings")

urlpatterns = [
    path("api/core/about/", views.AboutView.as_view(), name="version"),
    path("api/core/health/", views.HealthView.as_view(), name="health"),
    path("api/core/", include(router.urls)),
    path("api/core/", include(router_dd.urls)),
]
