"""URL patterns of the profiles extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from collectivo.utils.routers import DirectDetailRouter

from . import views

app_name = "collectivo.profiles"

router = DefaultRouter()
router.register("profiles", views.ProfileAdminViewSet, basename="profile")

self_router = DirectDetailRouter()
self_router.register("self", views.ProfileUserViewSet, basename="profile-self")

urlpatterns = [
    path("api/profiles/profiles/", include(self_router.urls)),
    path("api/profiles/", include(router.urls)),
]
