"""URL patterns of the collectivo authentication module."""
from django.urls import path
from collectivo.auth import views
from django.conf import settings


app_name = 'collectivo.auth'
urlpatterns = []

if settings.DEVELOPMENT:

    urlpatterns += [

        path(
            'api/dev/test_public/',
            views.PublicTestView.as_view(),
            name='test_view_public'
        ),
        path(
            'api/dev/test_private/',
            views.PrivateTestView.as_view(),
            name='test_view_private'
        ),
        path(
            'api/dev/test_admin/',
            views.AdminTestView.as_view(),
            name='test_view_admin'
        ),
        path(
            'api/dev/is_authenticated/',
            views.IsAuthenticatedView.as_view(),
            name='is_authenticated'),

        path('api/dev/token/',
             views.KeycloakTokenView.as_view(),
             name='token'),
    ]
