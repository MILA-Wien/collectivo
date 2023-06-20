"""URL patterns of the emails extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.emails"

router = DefaultRouter()
router.register("templates", views.EmailTemplateViewSet, basename="template")
router.register("campaigns", views.EmailCampaignViewSet, basename="campaign")
router.register("designs", views.EmailDesignViewSet, basename="design")
router.register("profiles", views.EmailProfileViewSet, basename="profile")
router.register(
    "automations", views.EmailAutomationViewSet, basename="automation"
)

urlpatterns = [
    path("api/emails/", include(router.urls)),
]
