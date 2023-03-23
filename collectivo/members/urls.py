"""URL patterns of the members extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from collectivo.utils.routers import DirectDetailRouter

from . import views

app_name = "collectivo.members"

admin_router = DefaultRouter()
admin_router.register("members", views.MembersViewSet, basename="member")
admin_router.register("memberships", views.MembershipViewSet)

me_router = DirectDetailRouter()
me_router.register(
    "register", views.MemberRegisterViewSet, basename="register"
)
me_router.register("profile", views.MemberProfileViewSet, basename="profile")

urlpatterns = [
    path("api/members/", include(admin_router.urls)),
    path("api/members/", include(me_router.urls)),
]
