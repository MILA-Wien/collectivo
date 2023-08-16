"""URL patterns of the emails extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.emails"

router = DefaultRouter()
router.register("templates", views.EmailTemplateViewSet, basename="template")
router.register("campaigns", views.EmailCampaignViewSet, basename="campaign")
router.register("designs", views.EmailDesignViewSet, basename="design")
router.register(
    "senderconfigs", views.EmailSenderConfigViewSet, basename="senderconfigs"
)
router.register("profiles", views.EmailProfileViewSet, basename="profile")
router.register(
    "automations", views.EmailAutomationViewSet, basename="automation"
)
router.register(
    "templates-history",
    views.EmailTemplateHistoryViewSet,
    basename="templates-history",
)
router.register(
    "campaigns-history",
    views.EmailCampaignHistoryViewSet,
    basename="campaign-history",
)
router.register(
    "designs-history",
    views.EmailDesignHistoryViewSet,
    basename="design-history",
)
router.register(
    "senderconfigs-history",
    views.EmailSenderConfigHistoryViewSet,
    basename="senderconfigs-history",
)
router.register(
    "automations-history",
    views.EmailAutomationHistoryViewSet,
    basename="automation-history",
)

urlpatterns = [
    path("api/emails/", include(router.urls)),
]
