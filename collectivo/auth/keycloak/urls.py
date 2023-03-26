"""URL patterns of the keycloak auth extension."""
from django.conf import settings
from django.urls import path

from . import views

app_name = "collectivo.auth.keycloak"

urlpatterns = []

if settings.DEVELOPMENT:
    urlpatterns += [
        path(
            "api/dev/token/", views.KeycloakTokenView.as_view(), name="token"
        ),
    ]
