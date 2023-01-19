"""URL patterns of the emails module."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'collectivo.members.emails'

router = DefaultRouter()
router.register('templates', views.EmailTemplateViewSet, basename='template')
router.register('campaigns', views.EmailCampaignViewSet, basename='campaign')
router.register('designs', views.EmailDesignViewSet, basename='design')

urlpatterns = [
    path('api/members/emails/', include(router.urls)),
]
