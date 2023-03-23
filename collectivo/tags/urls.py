"""URL patterns of the tags extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.tags"

router = DefaultRouter()
router.register("tags", views.TagViewSet)
router.register("categories", views.TagCategoryViewSet, basename="category")

urlpatterns = [
    path("api/tags/", include(router.urls)),
]
