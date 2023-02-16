"""Views of the user experience module."""

from datetime import datetime, time

import django_filters
from dateutil.parser import parse
from dateutil.rrule import FR, MO, MONTHLY, SA, SU, TH, TU, WE, rrule
from rest_framework import viewsets
from rest_framework.response import Response

from . import models, serializers


class ShiftFilter(django_filters.FilterSet):
    """Class to filter shifts."""

    # Commenting next line out, due to error:
    # Unsupported lookup 'icontains' for CharField
    # shift_title__icontains =
    # django_filters.CharFilter(lookup_expr="icontains")
    min_date = django_filters.DateFilter(
        field_name="starting_shift_date", lookup_expr="gte"
    )
    max_date = django_filters.DateFilter(
        field_name="starting_shift_date", lookup_expr="lte"
    )
    required_user = django_filters.NumberFilter(
        field_name="required_users", lookup_expr="gte"
    )
    shift_type = django_filters.CharFilter(field_name="shift_type")

    class Meta:
        """Meta class."""

        model = models.Shift
        fields = ["shift_week"]


class ShiftViewSet(viewsets.ModelViewSet):
    """Manage shifts."""

    queryset = models.Shift.objects.all()
    serializer_class = serializers.ShiftSerializer
    filterset_class = ShiftFilter

    # list(rrule(MONTHLY, byweekday=MO(1),
    # until=NOW+relativedelta(years=+2), dtstart=NOW))

    def get_queryset(self):
        """Manipulate queryset to filter."""
        queryset = models.Shift.objects.all()
        shift_title = self.request.query_params.get("shift_title__icontains")
        if shift_title is not None:
            queryset = queryset.filter(shift_title__icontains=shift_title)
        min_date = self.request.query_params.get("starting_shift_date__gte")
        if min_date is not None:
            queryset = queryset.filter(starting_shift_date__gte=min_date)
        max_date = self.request.query_params.get("starting_shift_date__lte")
        if max_date is not None:
            queryset = queryset.filter(starting_shift_date__lte=max_date)
        shift_type = self.request.query_params.get("shift_type")
        if shift_type is not None:
            queryset = queryset.filter(shift_type=shift_type)
        return queryset

    def list(self, request):
        """List all shifts."""
        # 1. Append unique shifts that are in bound of range
        # Get filtered queryset from get_queryset()
        queryset = self.get_queryset()
        response = []
        for shift in queryset:
            response.append(serializers.ShiftSerializer(shift).data)
        print("Response with unique shifts", response)

        # 2. Append regular shifts that are in bound of range
        # Get queryset of regular shifts
        queryset_regular = models.Shift.objects.filter(shift_type="regular")

        # Check if params are set that user filters by min/max_date
        if request.query_params.get(
            "starting_shift_date__gte"
        ) and request.query_params.get("starting_shift_date__lte"):
            min_date = request.query_params.get("starting_shift_date__gte")

            max_date = request.query_params.get("starting_shift_date__lte")

            # Check if there are regular shifts that started before min_date
            if queryset_regular.filter(starting_shift_date__lte=min_date):
                # Filter queryset to only include regular shifts
                # that started before min_date
                queryset_regular = queryset_regular.filter(
                    starting_shift_date__lte=min_date
                )
                # Calculate when regular shift occurs during min/max_date
                for shift in queryset_regular:
                    # TODO using parameters from shift
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
                    week_number = week_dict[shift.shift_week]
                    weekday = weekday_dict[shift.shift_day]
                    print("Weeek number", week_number)
                    print("Weekday", weekday)
                    print(
                        "Occurences list",
                        list(
                            rrule(
                                MONTHLY,
                                byweekday=weekday,
                                byweekno=[x for x in range(week_number, 52, 4)],
                                dtstart=parse(
                                    min_date + "T00:00:00",
                                ),
                                until=parse(
                                    max_date + "T00:00:00",
                                ),
                            )
                        ),
                    )

                    occurences = list(
                        rrule(
                            MONTHLY,
                            byweekday=weekday,
                            byweekno=[x for x in range(week_number, 52, 4)],
                            dtstart=parse(
                                min_date + "T00:00:00",
                            ),
                            until=parse(
                                max_date + "T00:00:00",
                            ),
                        )
                    )

                    # Create virtual shift by adding 1-2 occurrence(s) to shift
                    for occurence in occurences:
                        print("occurence", occurence)
                        # Assign date of occurence to shift
                        shift.starting_shift_date = occurence.date()
                        # Append virtual shift to list
                        response.append(
                            serializers.ShiftSerializer(shift).data,
                        )

                # 4. Return list of shifts including virtual shifts
                return Response(response)


class AssignmentViewSet(viewsets.ModelViewSet):
    """Manage individual shifts."""

    queryset = models.Assignment.objects.all()
    serializer_class = serializers.AssignmentSerializer


class ShiftUserViewSet(viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftUser.objects.all()
    serializer_class = serializers.ShiftUserSerializer
