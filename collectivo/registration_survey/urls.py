"""URL patterns of the registration_survey extension."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "collectivo.registration_survey"

router = DefaultRouter()
router.register("profiles", views.SurveyProfileViewSet)
router.register("skills", views.SurveyGroupViewSet)
router.register("groups", views.SurveySkillViewSet)


urlpatterns = [
    path("api/registration_survey/", include(router.urls)),
]
