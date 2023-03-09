"""URL patterns of the extension."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirektkreditViewSet


app_name = "collectivo.direktkredit"

# router = DefaultRouter()
# router.register('direktkreditmodel', DirektkreditViewSet)


urlpatterns = [
    # path('api/direktkredit/', include(router.urls)),
]
