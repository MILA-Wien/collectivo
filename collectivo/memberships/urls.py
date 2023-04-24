"""URL patterns of the memberships extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.memberships"

router = DefaultRouter()
router.register("memberships", views.MembershipAdminViewSet)
router.register("types", views.MembershipTypeViewSet)
router.register("statuses", views.MembershipStatusViewSet, basename="status")

self_router = DefaultRouter()
self_router.register(
    "self", views.MembershipUserViewSet, basename="membership-self"
)

urlpatterns = [
    path("api/memberships/memberships/", include(self_router.urls)),
    path("api/memberships/", include(router.urls)),
]
