"""URL patterns of the devtools."""
from django.urls import path
from . import views


app_name = 'collectivo.devtools'
api_path = f'api/{app_name}/'

urlpatterns = [
    path('api/dev/test/', views.TestAPIView.as_view(), name='test_api'),
    path('dev/', views.test_html_view, name='test_html'),
]
