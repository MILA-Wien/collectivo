"""Utility functions of the dashboard module."""
from collectivo.utils import register_viewset
from . import views


def register_tag(**payload):
    """Register a dashboard tile."""
    return register_viewset(views.MemberTagViewSet, payload=payload,
                            allow_bad_response=True)


def register_skill(**payload):
    """Register a dashboard tile."""
    return register_viewset(views.MemberSkillViewSet, payload=payload,
                            allow_bad_response=True)


def register_group(**payload):
    """Register a dashboard tile."""
    return register_viewset(views.MemberGroupViewSet, payload=payload,
                            allow_bad_response=True)
