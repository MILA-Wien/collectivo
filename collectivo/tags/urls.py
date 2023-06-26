"""URL patterns of the tags extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.tags"

router = DefaultRouter()
router.register(
    "tags-history", views.TagHistoryViewSet, basename="tag-history"
)
router.register("tags", views.TagViewSet)
router.register("profiles", views.TagProfileViewSet, basename="profile")

urlpatterns = [
    path("api/tags/", include(router.urls)),
]
