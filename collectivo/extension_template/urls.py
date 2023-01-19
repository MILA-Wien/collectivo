"""URL patterns of the extension."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyModelViewSet


app_name = 'collectivo.extension_template'

router = DefaultRouter()
router.register('mymodel', MyModelViewSet)


urlpatterns = [
    path('api/extension_template/', include(router.urls)),
]
