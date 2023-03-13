"""Views of the user experience module."""

from datetime import datetime

import django_filters
from dateutil.parser import parse
from dateutil.rrule import FR, MO, MONTHLY, SA, SU, TH, TU, WE, rrule
from django.forms import ValidationError
from rest_framework import viewsets
from rest_framework.response import Response

from . import models, serializers


class ShiftFilter(django_filters.FilterSet):
    """Class to filter shifts."""

    class Meta:
        """Meta class."""

        model = models.Shift
        fields = "__all__"


class ShiftViewSet(viewsets.ModelViewSet):
    """Manage shifts."""

    queryset = models.Shift.objects.all()
    serializer_class = serializers.ShiftSerializer
    filterset_class = ShiftFilter

    def custom_filter(self, queryset):
        """Filter all parameters excluding shift_starting_date."""
        # TODO use integrated filter instead of manual filter
        shift_title = self.request.query_params.get("shift_title__icontains")
        if shift_title is not None:
            queryset = queryset.filter(shift_title__icontains=shift_title)
        shift_type = self.request.query_params.get("shift_type")
        if shift_type is not None:
            queryset = queryset.filter(shift_type=shift_type)
        shift_week = self.request.query_params.get("shift_week")
        if shift_week is not None:
            queryset = queryset.filter(shift_week=shift_week)
        shift_starting_time = self.request.query_params.get(
            "shift_starting_time",
        )
        if shift_starting_time is not None:
            queryset = queryset.filter(shift_starting_time=shift_starting_time)
        shift_ending_time = self.request.query_params.get("shift_ending_time")
        if shift_ending_time is not None:
            queryset = queryset.filter(shift_ending_time=shift_ending_time)
        required_users = self.request.query_params.get("required_users")
        if required_users is not None:
            queryset = queryset.filter(required_users=required_users)
        shift_day = self.request.query_params.get("shift_day")
        if shift_day is not None:
            queryset = queryset.filter(shift_day=shift_day)
        additional_info_general = self.request.query_params.get(
            "additional_info_general"
        )
        if additional_info_general is not None:
            queryset = queryset.filter(
                additional_info_general=additional_info_general,
            )
        return queryset

    def get_queryset(self):
        """Manipulate queryset to filter."""
        queryset = models.Shift.objects.all()

        min_date = self.request.query_params.get("shift_starting_date__gte")
        if min_date is not None:
            queryset = queryset.filter(shift_starting_date__gte=min_date)
        max_date = self.request.query_params.get("shift_starting_date__lte")
        if max_date is not None:
            queryset = queryset.filter(shift_starting_date__lte=max_date)

        queryset = self.custom_filter(queryset)

        return queryset

    def create_virtual_shifts(self, queryset, response, min_date, max_date):
        """Create virtual shifts for regular shifts."""
        # Create dictionaries for translation to rrule parameters
        week_dict = {"A": 1, "B": 2, "C": 3, "D": 4}
        weekday_dict = {
            "Monday": MO,
            "Tuesday": TU,
            "Wednesday": WE,
            "Thursday": TH,
            "Friday": FR,
            "Saturday": SA,
            "Sunday": SU,
        }
        # Loop through all shifts in queryset
        for shift in queryset.iterator():
            # Assign week number and weekday from shift
            week_number = week_dict[shift.shift_week]
            weekday = weekday_dict[shift.shift_day]

            # Check if starting shift date is after min_date
            if (
                shift.shift_starting_date
                and shift.shift_starting_date
                > datetime.strptime(min_date, "%Y-%m-%d").date()
            ):
                min_date = shift.shift_starting_date.strftime("%Y-%m-%d")

            # Check if ending shift date is before max_date
            if (
                shift.shift_ending_date
                and shift.shift_ending_date
                < datetime.strptime(max_date, "%Y-%m-%d").date()
            ):
                max_date = shift.shift_ending_date.strftime("%Y-%m-%d")
            # Calculate occurrences in given date range
            # Docs rrule: https://dateutil.readthedocs.io/en/stable/rrule.html
            # Docs range: https://docs.python.org/3/library/stdtypes.html#range
            occurrences = list(
                rrule(
                    MONTHLY,
                    byweekday=weekday,
                    byweekno=[
                        x
                        for x in range(
                            week_number,
                            52,
                            4,
                        )
                    ],
                    dtstart=parse(
                        min_date + "T00:00:00",
                    ),
                    until=parse(
                        max_date + "T00:00:00",
                    ),
                )
            )

            if not occurrences:
                # If no occurrences in shift, continue to next shift
                continue
            else:
                # Loop 1-2 times in monthly scenario for occurrences
                for occurrence in occurrences:
                    # Assign date of occurrence to shift
                    shift.shift_starting_date = occurrence.date()
                    # Append virtual shift to list
                    response.append(
                        serializers.ShiftSerializer(shift).data,
                    )
        return response

    def list(self, request):
        """List all shifts."""
        # Get filtered queryset from get_queryset()
        queryset = self.get_queryset()
        response = []
        # !! Assumes both parameters are always given, if not error occurs !!
        min_date = request.query_params.get("shift_starting_date__gte")
        if not min_date:
            raise ValidationError(
                "Missing attribute 'shift_starting_date__gte'"
            )
        max_date = request.query_params.get("shift_starting_date__lte")
        if not max_date:
            raise ValidationError(
                "Missing attribute 'shift_starting_date__lte'"
            )
        # Get all regular shifts
        queryset_regular = models.Shift.objects.filter(
            shift_type="regular",
        )

        # 1. Append unique shifts that are in bound of range
        if queryset.filter(shift_type="unique").exists():
            queryset_unique = queryset.filter(shift_type="unique")
            for shift in queryset_unique.iterator():
                response.append(serializers.ShiftSerializer(shift).data)

        # 2. Append regular shifts that are in bound of range
        if queryset.filter(shift_type="regular").exists():
            queryset = queryset.filter(shift_type="regular")
            response = self.create_virtual_shifts(
                queryset, response, min_date, max_date
            )

        # 3. Append regular shifts that started before min_date
        # and fulfill all other parameters
        # TODO use filter class instead of manually filtering
        if (
            queryset_regular.filter(
                shift_starting_date__lt=min_date,
            ).exists()
            and self.custom_filter(queryset_regular).exists()
        ):
            queryset_regular = self.custom_filter(queryset_regular)
            queryset_regular = queryset_regular.filter(
                shift_starting_date__lt=min_date,
            )
            response = self.create_virtual_shifts(
                queryset_regular,
                response,
                min_date,
                max_date,
            )

        # 4. Return list of shifts including shifts with virtual dates
        return Response(response)


class AssignmentViewSet(viewsets.ModelViewSet):
    """Manage individual shifts."""

    queryset = models.Assignment.objects.all()
    serializer_class = serializers.AssignmentSerializer


class ShiftUserViewSet(viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftUser.objects.all()
    serializer_class = serializers.ShiftUserSerializer
