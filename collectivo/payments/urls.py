"""URL patterns of the extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from .views import MyModelViewSet

app_name = "collectivo.extension_template"

router = DefaultRouter()
# router.register("mymodel", MyModelViewSet, basename="XY")


urlpatterns = [
    path("api/extension_template/", include(router.urls)),
]
