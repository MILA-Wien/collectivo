"""URL patterns of the emails module."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "collectivo.payments"

router = DefaultRouter()
router.register("payments", views.PaymentViewSet)
router.register("subscriptions", views.SubscriptionViewSet)


urlpatterns = [
    path("api/payments/", include(router.urls)),
]
