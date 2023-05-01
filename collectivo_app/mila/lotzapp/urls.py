"""URL patterns of the extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from collectivo.utils.routers import DirectDetailRouter
from . import views

app_name = "mila.lotzapp"


router = DefaultRouter()
router.register("invoices", views.LotzappInvoiceViewSet, basename="invoice")
router.register("addresses", views.LotzappAddressViewSet, basename="address")

srouter = DirectDetailRouter()
srouter.register("settings", views.LotzappSettingsViewSet, basename="settings")

urlpatterns = [
    path("api/lotzapp/", include(router.urls)),
    path("api/lotzapp/", include(srouter.urls)),
]
