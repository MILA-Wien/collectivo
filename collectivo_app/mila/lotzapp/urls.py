"""URL patterns of the extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "mila.lotzapp"


router = DefaultRouter()
router.register("invoices", views.LotzappInvoiceViewSet, basename="invoice")
router.register("addresses", views.LotzappAddressViewSet, basename="address")

urlpatterns = [path("api/lotzapp/", include(router.urls))]
