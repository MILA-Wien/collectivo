"""Models of the registration_survey extension."""
from django.contrib.auth import get_user_model
from django.db import models

from collectivo.utils.managers import NameManager


class SurveySkill(models.Model):
    """A skill that can be selected in the survey."""

    objects = NameManager()
    name = models.CharField(max_length=255)

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class SurveyGroup(models.Model):
    """A group that can be selected in the survey."""

    objects = NameManager()
    name = models.CharField(max_length=255)

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class SurveyProfile(models.Model):
    """Extend the user profile with a custom registration survey."""

    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="registration_survey",
    )

    survey_contact = models.TextField(null=True, blank=True)
    survey_motivation = models.TextField(null=True, blank=True)
    groups_interested = models.ManyToManyField(
        "SurveyGroup", related_name="groups_interested", blank=True
    )
    skills = models.ManyToManyField("SurveySkill", blank=True)
