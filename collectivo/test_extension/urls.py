"""Urls patterns of the test extension."""
from django.urls import path
from extensions import views

app_name = 'test_extension'


urlpatterns = [
    path('', views.GetExtensions.as_view(), name='test_view'),
]
