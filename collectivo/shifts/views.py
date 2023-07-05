"""Views of the user experience module."""

from datetime import date, datetime

import django_filters
from dateutil.parser import parse
from dateutil.rrule import FR, MO, MONTHLY, SA, SU, TH, TU, WE, rrule
from django.db.models import Q
from django.forms import ValidationError
from rest_framework import viewsets
from rest_framework.response import Response

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import SchemaMixin
from collectivo.utils.permissions import HasPerm

from . import models, serializers
from .abcd import get_abcd_occurences


# TODO: Add permission_classes
def weeknumber_to_abcd(weeknumber: int) -> str:
    """Convert a weeknumber to an ABCD week."""
    return "ABCD"[(weeknumber - 1) % 4]


class ShiftFilter(django_filters.FilterSet):
    """Class to filter shifts."""

    class Meta:
        """Meta class."""

        model = models.Shift
        fields = "__all__"


class ShiftSelfViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage shifts."""

    serializer_class = serializers.ShiftSerializer
    filterset_class = ShiftFilter

    def get_queryset(self):
        """Get all shifts for the current user."""
        return models.Shift.objects.filter(
            slots__user=self.request.user,
        )


class ShiftViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage shifts (that can have multiple occurences)."""

    queryset = models.Shift.objects.all()
    serializer_class = serializers.ShiftSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_shifts", "core")],
        "ALL": [("edit_shifts", "core")],
    }
    filterset_class = get_filterset(serializers.ShiftSerializer)
    ordering_fields = get_ordering_fields(serializers.ShiftSerializer)


class ShiftOccurenceViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage shift occurences (with a specific date)."""

    queryset = models.Shift.objects.all()
    serializer_class = serializers.ShiftSerializer
    filterset_class = ShiftFilter

    def create_abcd_occurences(self, queryset, response, min_date, max_date):
        """Generate shift occurences for repeating ABCD shifts."""

        # Loop through all shifts in queryset
        for shift in queryset.iterator():
            # # Check if starting shift date is after min_date
            # if shift.repeat_start and shift.repeat_start > min_date:
            #     min_date = shift.repeat_start.strftime("%Y-%m-%d")

            # # Check if ending shift date is before max_date
            # if shift.repeat_end and shift.repeat_end < max_date:
            #     max_date = shift.repeat_end.strftime("%Y-%m-%d")

            # Calculate occurrences in given date range
            # Docs rrule: https://dateutil.readthedocs.io/en/stable/rrule.html
            # Docs range: https://docs.python.org/3/library/stdtypes.html#range
            occurrences = list(
                get_abcd_occurences(
                    shift.abcd_week, shift.abcd_day, min_date, max_date
                )
            )

            if not occurrences:
                # If no occurrences in shift, continue to next shift
                continue
            else:
                # Loop 1-2 times in monthly scenario for occurrences
                for occurrence in occurrences:
                    # Assign date of occurrence to shift
                    date = occurrence.date().isocalendar()
                    shift.date = occurrence.date()
                    # Append virtual shift to list
                    shift_data = serializers.ShiftSerializer(shift).data
                    if date[1] not in response:
                        response[date.week] = [[] for i in range(7)]
                    response[date.week][date.weekday - 1].append(shift_data)

        return response

    def list(self, request):
        """List all shifts."""
        queryset = self.get_queryset()
        response = {}

        # Read out parameters from request
        params = {"year": None, "from": None, "to": None}
        for param in params:
            params[param] = int(request.query_params.get(param))
            if not params[param]:
                raise ValidationError(f"Missing attribute '{param}'")
        min_date = date.fromisocalendar(params["year"], params["from"], 1)
        max_date = date.fromisocalendar(params["year"], params["to"], 7)
        min_date_iso = min_date.isocalendar()
        max_date_iso = max_date.isocalendar()

        # 1. Append unique shifts that are in bound of range
        queryset_unique = queryset.filter(
            repeat="none", date__gte=min_date, date__lte=max_date
        )
        for shift in queryset_unique.iterator():
            iso_date = shift.date.isocalendar()
            if iso_date[1] not in response:
                response[iso_date.week] = [[] for i in range(7)]
            response[iso_date.week][iso_date.weekday - 1].append(
                serializers.ShiftSerializer(shift).data
            )

        # 2. Append regular shifts that are in bound of range
        queryset_abcd = queryset.filter(
            Q(repeat="abcd"),
            (Q(repeat_start=None) | Q(repeat_start__lte=max_date)),
            (Q(repeat_end=None) | Q(repeat_end__gte=min_date)),
        )
        if queryset_abcd.exists():
            response = self.create_abcd_occurences(
                queryset_abcd, response, min_date, max_date
            )

        # 3. Return list of shift occurences, sorted into weeks and days
        list_response = [
            {
                "weeknumber": week,
                "days": [
                    {
                        "shifts": response[week][day]
                        if week in response
                        else [],
                        "date": date.fromisocalendar(
                            min_date_iso.year, week, day + 1
                        ),
                    }
                    for day in range(7)
                ],
                "abcd": weeknumber_to_abcd(week),
            }
            for week in range(min_date_iso.week, max_date_iso.week + 1)
        ]
        for week in list_response:
            for day in week["days"]:
                day["shifts"].sort(key=lambda x: x["starting_time"])

        return Response(list_response)


class ShiftOccurenceOpenViewSet(ShiftOccurenceViewSet):
    """Manage shift occurences with open slots."""

    def get_queryset(self):
        """Return only shifts with open slots."""
        open_slots = models.ShiftSlot.objects.filter(user__isnull=True)
        return super().get_queryset().filter(slots__in=open_slots)


class ShiftSlotViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage shift slots that can be assigned to a user."""

    queryset = models.ShiftSlot.objects.all()
    serializer_class = serializers.ShiftSlotSerializer
    # Todo users should only be able to see their own assignments
    # TODO users should only be able to create assignments for themselves
    # TODO users should only be able to update assignments for themselves
    # TODO users should only be able to delete assignments for themselves
    # TODO users should only be able to update the following fields:
    # - assged_user
    # - additional_info_individual
    # TODO users shouldn't be able to delete the object
    # TODO on monthly/weekly shifts, the user should only be able to update
    #   the following fields:
    #  - replacement_user
    #  - additional_info_individual
    #  - open_for_replacement


class ShiftUserViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftProfile.objects.all()
    serializer_class = serializers.ShiftUserSerializer


class ShiftProfileSelfViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage self user."""

    serializer_class = serializers.ShiftUserSerializer
    # TODO create user if not exists

    def get_queryset(self):
        """Get all shifts for the current user."""
        result = models.ShiftProfile.objects.filter(
            user=self.request.user,
        )
        if not result:
            models.ShiftProfile.objects.create(user=self.request.user)
            result = models.ShiftProfile.objects.filter(
                user=self.request.user,
            )
        return result
