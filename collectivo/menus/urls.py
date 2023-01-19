"""URL patterns of the user experience module."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'collectivo.menus'

router = DefaultRouter()
router.register('menus', views.MenuViewSet)
router.register(
    r'menus/(?P<menu_id>\w+)/items',
    views.MenuItemViewSet,
    basename='menuitem'
)

urlpatterns = [
    path('api/menus/', include(router.urls)),
]
