"""URL Configuration of collectivo_app."""
from django.urls import path, include


urlpatterns = [path('', include('collectivo.urls'))]

handler400 = 'rest_framework.exceptions.bad_request'
handler500 = 'rest_framework.exceptions.server_error'
