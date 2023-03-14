"""Utility functions of the emails module."""
from . import views
from collectivo.utils import register_viewset


def register_email_template(**payload):
    """Register an email template."""
    return register_viewset(views.EmailTemplateViewSet, payload=payload)


def register_email_design(**payload):
    """Register an email design."""
    return register_viewset(views.EmailDesignViewSet, payload=payload)
