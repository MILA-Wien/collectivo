"""URL Configuration of collectivo_app."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("collectivo.urls")),
    # TODO: Move this to MILA Repository
    path("", include("mila.registration.urls")),
    path("", include("mila.lotzapp.urls")),
]

handler400 = "rest_framework.exceptions.bad_request"
handler500 = "rest_framework.exceptions.server_error"
