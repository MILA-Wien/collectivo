"""URL patterns of the MILA registration extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from collectivo.utils.routers import DirectDetailRouter

from . import views

app_name = "mila.registration"

router = DefaultRouter()
router.register("profiles", views.SurveyProfileViewSet)
router.register("skills", views.SurveySkillViewSet)
router.register("groups", views.SurveyGroupViewSet)


me_router = DirectDetailRouter()
me_router.register("register", views.MilaRegisterViewSet, basename="register")

urlpatterns = [
    path("api/mila/", include(router.urls)),
    path("api/mila/", include(me_router.urls)),
]
