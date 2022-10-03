"""URL patterns of the collectivo core."""
from django.urls import path, include
from collectivo import views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)


app_name = 'collectivo'


urlpatterns = [
    path('api/version/', views.GetVersion.as_view(), name='version'),

    path('api/user/', include('collectivo.user.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/',
         SpectacularSwaggerView.as_view(url_name='collectivo:api-schema'),
         name='api-docs'),
]
