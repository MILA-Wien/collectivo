"""URL patterns of the user experience module."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.shifts"

router = DefaultRouter()
router.register(
    "shifts",
    views.ShiftViewSet,
    basename="shift",
)
router.register(
    "assignments",
    views.AssignmentViewSet,
    basename="assignment",
)
router.register("shift-users", views.ShiftUserViewSet, basename="shift-user")

self_router = DefaultRouter()
self_router.register("", views.ShiftSelfViewSet, basename="shift-self")

urlpatterns = [
    path("api/shifts/shifts/self/", include(self_router.urls)),
    path("api/shifts/", include(router.urls)),
]
