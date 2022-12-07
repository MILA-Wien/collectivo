"""Utility functions of the collectivo package."""
from django.test import RequestFactory
from django.conf import settings
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from collectivo.auth.userinfo import UserInfo
import logging
import importlib


logger = logging.getLogger(__name__)


# https://docs.djangoproject.com/en/4.1/ref/models/querysets/#field-lookups
filter_lookups = [
    'exact', 'iexact', 'contains', 'icontains', 'in', 'gt', 'gte',
    'lt', 'lte', 'startswith', 'istartswith', 'endswith', 'iendswith',
    'range',  # 'date', 'year', 'iso_year', 'month', 'day', 'week',
    # 'week_day', 'iso_week_day', 'quarter', 'time', 'hour', 'minute',
    # 'second', 'isnull', 'regex', 'iregex',
]


# Retrieve default models as defined in the settings
# Can be used to access models without creating dependencies

def get_object_from_settings(setting_name):
    """Return a default model as defined in the settings."""
    cls = settings.COLLECTIVO[setting_name]
    module_name, class_name = cls.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def get_auth_manager():
    """Return default auth manager object."""
    return get_object_from_settings('default_auth_manager')()


def get_user_model():
    """Return default user object."""
    return get_object_from_settings('default_user_model')


def get_extension_model():
    """Return default extension object."""
    return get_object_from_settings('default_extension_model')


# Internal API calls
# Can be used for extensions to communicate via REST API

def request(viewset: ViewSet, command='create', payload=None,
            userinfo=None, **kwargs) -> Response:
    """Make an internal http request to a DRF Viewset."""
    rf = RequestFactory()
    drf_to_http = {
        'create': 'post',
        'update': 'put',
        'retrieve': 'get',
        'list': 'get',
        'destroy': 'delete',
    }

    method = drf_to_http[command]

    request = getattr(rf, method)(
        None, payload, content_type="application/json")

    if userinfo is not None:
        request.userinfo = userinfo
    else:
        request.userinfo = UserInfo(roles=['superuser'])

    response = viewset.as_view({method: command})(request, **kwargs)

    return response


def register_viewset(
        viewset, pk=None, payload=None, userinfo=None,
        allow_bad_response=False) -> Response:
    """Register a viewset."""
    # TODO Improve logic
    get = None
    if pk is not None and hasattr(viewset, 'retrieve'):
        get = request(viewset, 'retrieve', payload, userinfo, pk=pk)
    if get is not None and get.status_code == 200:
        response = request(viewset, 'update', payload, userinfo, pk=pk)
    else:
        response = request(viewset, 'create', payload, userinfo)
    if response.status_code not in [200, 201] and not allow_bad_response:
        response.render()
        logger.warning(
            f"Could not register viewset '{viewset}'. "
            f"{response.status_code}: {response.content}"
        )
    return response
