"""URL patterns of the user experience module."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'collectivo.shifts'

router = DefaultRouter()
router.register('shifts', views.ShiftViewSet)

urlpatterns = [
    path('api/shifts/', include(router.urls)),
]
