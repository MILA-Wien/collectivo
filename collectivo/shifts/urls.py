"""URL patterns of the user experience module."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.shifts"

router = DefaultRouter()
router.register(
    "general-shifts",
    views.GeneralShiftViewSet,
    basename="general-shift",
)
router.register(
    "individual-shifts",
    views.IndividualShiftViewSet,
    basename="individual-shift",
)
router.register("shift-users", views.ShiftUserViewSet, basename="shift-user")


urlpatterns = [
    path("api/shifts/", include(router.urls)),
]
