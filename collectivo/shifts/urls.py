"""URL patterns of the user experience module."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.shifts"

router = DefaultRouter()
router.register(
    "shifts",
    views.ShiftViewSet,
)
router.register(
    "occurences",
    views.ShiftOccurenceViewSet,
    basename="occurence",
)
router.register(
    "slots",
    views.ShiftSlotViewSet,
)
router.register("users", views.ShiftUserViewSet, basename="shift-user")

self_router = DefaultRouter()
self_router.register("", views.ShiftSelfViewSet, basename="shift-self")

self_user_router = DefaultRouter()
self_user_router.register(
    "", views.ShiftProfileSelfViewSet, basename="shift-user-self"
)

open_router = DefaultRouter()
open_router.register(
    "", views.ShiftOccurenceOpenViewSet, basename="occurence-open"
)

urlpatterns = [
    path("api/shifts/shifts/self/", include(self_router.urls)),
    path("api/shifts/user/self/", include(self_user_router.urls)),
    path("api/shifts/occurences/open/", include(open_router.urls)),
    path("api/shifts/", include(router.urls)),
]
