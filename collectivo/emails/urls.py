"""URL patterns of the emails module."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'collectivo.emails'

router = DefaultRouter()
router.register('templates', views.EmailTemplateViewSet)
router.register('logs', views.EmailBatchViewSet)

urlpatterns = [
    path('api/emails/', include(router.urls)),
]
