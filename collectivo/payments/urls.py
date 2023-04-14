"""URL patterns of the payments module."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from collectivo.utils.routers import DirectDetailRouter

from . import views

app_name = "collectivo.payments"

router = DefaultRouter()
router.register("profiles", views.ProfileViewSet)
router.register("invoices", views.InvoiceViewSet)
router.register("subscriptions", views.SubscriptionViewSet)

me_router = DirectDetailRouter()
me_router.register("self", views.ProfileSelfViewSet, basename="profile-self")

urlpatterns = [
    path("api/payments/profiles/", include(me_router.urls)),
    path("api/payments/", include(router.urls)),
]
