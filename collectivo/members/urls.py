"""URL patterns of the members extension."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from collectivo.routers import DirectDetailRouter
from . import views


app_name = 'collectivo.members'

router1 = DefaultRouter()
router1.register('members', views.MembersViewSet, basename='member')
router1.register('summary', views.MembersSummaryViewSet, basename='summary')
router1.register('tags', views.MemberTagViewSet, basename='tag')
router1.register('skills', views.MemberSkillViewSet, basename='skill')
router1.register('groups', views.MemberGroupViewSet, basename='group')
router1.register('status', views.MemberStatusViewSet, basename='status')

router2 = DirectDetailRouter()
router2.register('register', views.MemberRegisterViewSet, basename='register')
router2.register('profile', views.MemberProfileViewSet, basename='profile')

urlpatterns = [
    path('api/members/', include(router1.urls)),
    path('api/members/', include(router2.urls)),
]
