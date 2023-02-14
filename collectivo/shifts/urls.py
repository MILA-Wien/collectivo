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


urlpatterns = [
    path("api/shifts/", include(router.urls)),
]
