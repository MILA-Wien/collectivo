"""URL patterns of the members extension."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from collectivo.routers import DirectDetailRouter
from . import views


app_name = 'collectivo.members'

router = DefaultRouter()
router.register('members', views.MembersViewSet, basename='member')
router.register('summary', views.MembersSummaryViewSet, basename='summary')
router.register('tags', views.MemberTagViewSet, basename='tag')
router.register('skills', views.MemberSkillViewSet, basename='skill')
router.register('groups', views.MemberGroupViewSet, basename='group')
router.register('status', views.MemberStatusViewSet, basename='status')

me_router = DirectDetailRouter()
me_router.register('register', views.MemberRegisterViewSet, basename='register')
me_router.register('profile', views.MemberProfileViewSet, basename='profile')

urlpatterns = [
    path('api/members/', include(router.urls)),
    path('api/members/', include(me_router.urls)),
]
