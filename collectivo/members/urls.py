"""URL patterns of the members extension."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from collectivo.routers import DirectDetailRouter
from . import views


app_name = 'collectivo.members'

admin_router = DefaultRouter()
admin_router.register(
    'members', views.MembersAdminViewSet, basename='member')
admin_router.register(
    'create', views.MembersAdminCreateViewSet, basename='create')
admin_router.register(
    'summary', views.MembersSummaryViewSet, basename='summary')
admin_router.register(
    'groups', views.MemberGroupViewSet, basename='group')
admin_router.register(
    'skills', views.MemberSkillViewSet, basename='skill')
admin_router.register(
    'tags', views.MemberTagViewSet, basename='tag')

me_router = DirectDetailRouter()
me_router.register(
    'register', views.MemberRegisterViewSet, basename='register')
me_router.register(
    'profile', views.MemberProfileViewSet, basename='profile')

urlpatterns = [
    path('api/members/', include(admin_router.urls)),
    path('api/members/', include(me_router.urls)),
]
