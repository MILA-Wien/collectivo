"""URL patterns of the dashboard extension."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardTileViewSet


app_name = 'collectivo.dashboard'

router = DefaultRouter()
router.register('tiles', DashboardTileViewSet)


urlpatterns = [
    path('api/dashboard/v1/', include(admin_router.urls)),
]
