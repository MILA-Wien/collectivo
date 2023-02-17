"""Views of the user experience module."""

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

    def custom_filter(self, queryset):
        """Filter all parameters excluding starting_shift_date."""
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

        min_date = self.request.query_params.get("starting_shift_date__gte")
        if min_date is not None:
            queryset = queryset.filter(starting_shift_date__gte=min_date)
        max_date = self.request.query_params.get("starting_shift_date__lte")
        if max_date is not None:
            queryset = queryset.filter(starting_shift_date__lte=max_date)

        queryset = self.custom_filter(queryset)

        return queryset

    def list(self, request):
        """List all shifts."""
        # 1. Append unique shifts that are in bound of range
        # Get filtered queryset from get_queryset()
        queryset = self.get_queryset()
        response = []

        # Add shifts from filtered queryset to response
        if queryset.exists():
            for shift in queryset.iterator():
                response.append(serializers.ShiftSerializer(shift).data)

        if request.query_params.get(
            "starting_shift_date__gte"
        ) and request.query_params.get("starting_shift_date__lte"):
            # 2. Append regular shifts that are in bound of range
            # Get queryset of regular shifts
            queryset_regular = models.Shift.objects.filter(
                shift_type="regular",
            )
            # Filter queryset to all parameters besides starting_shift_date
            # since we want to calculate the occurence of the regular shift
            # TODO use filter class instead of manually filtering
            queryset_regular = self.custom_filter(queryset_regular)
            if queryset_regular.exists():
                # Check if user filters by min/max_date and
                min_date = request.query_params.get("starting_shift_date__gte")

                max_date = request.query_params.get("starting_shift_date__lte")

                # Check if regular shifts exist that started before min_date
                if queryset_regular.filter(
                    starting_shift_date__lte=min_date,
                ).exists():
                    # Filter queryset to only include regular shifts
                    # that started before min_date
                    queryset_regular3 = queryset_regular.filter(
                        starting_shift_date__lte=min_date
                    )
                    # Calculate when regular shift occurs during min/max_date
                    for shift in queryset_regular3:
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
                        # Assign week number and weekday from shift
                        week_number = week_dict[shift.shift_week]
                        weekday = weekday_dict[shift.shift_day]
                        occurences = list(
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

                        # Loop 1 or 2 times through each occurrence
                        for occurence in occurences:
                            # Assign date of occurence to shift
                            shift.starting_shift_date = occurence.date()
                            # Append virtual shift to list
                            response.append(
                                serializers.ShiftSerializer(shift).data,
                            )

        # 4. Return list of shifts including virtual shifts
        # for shift in response[0]:
        #     print("SHIT", shift.id)
        print(response)
        return Response(response)


class AssignmentViewSet(viewsets.ModelViewSet):
    """Manage individual shifts."""

    queryset = models.Assignment.objects.all()
    serializer_class = serializers.AssignmentSerializer


class ShiftUserViewSet(viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftUser.objects.all()
    serializer_class = serializers.ShiftUserSerializer
