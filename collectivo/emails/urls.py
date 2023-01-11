"""URL patterns of the emails module."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'collectivo.emails'

router = DefaultRouter()
router.register('templates', views.EmailTemplateViewSet, basename='template')
router.register('batches', views.EmailCampaignViewSet, basename='batch')
router.register('designs', views.EmailDesignViewSet, basename='design')

urlpatterns = [
    path('api/emails/', include(router.urls)),
]
