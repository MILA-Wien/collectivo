"""Urls patterns of the extensions app."""
from django.urls import path
from extensions import views


app_name = 'extensions'

urlpatterns = [
    path('', views.GetExtensions.as_view(), name='extensions'),
]
