"""URL patterns of the user experience module."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.menus"

router = DefaultRouter()
router.register("menus", views.MenuViewSet)
router.register("items", views.MenuItemViewSet)

urlpatterns = [
    path("api/menus/", include(router.urls)),
]
