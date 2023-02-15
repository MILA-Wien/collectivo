"""Views of the user experience module."""

import django_filters
from dateutil.parser import parse
from dateutil.rrule import MO, MONTHLY, rrule
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
        queryset = self.get_queryset()

        queryset_regular = models.Shift.objects.filter(shift_type="regular")

        if request.query_params.get(
            "starting_shift_date__gte"
        ) and request.query_params.get("starting_shift_date__lte"):
            min_date = request.query_params.get("starting_shift_date__gte")
            # check if there are regular shifts that started before min_date
            if queryset_regular.filter(starting_shift_date__lte=min_date):
                queryset_regular = queryset_regular.filter(
                    starting_shift_date__lte=min_date
                )
                for shift in queryset_regular:
                    # 1. calculate when regular shift occurs during this month
                    print([x for x in range(1, 52, 4)])
                    print(
                        list(
                            rrule(
                                MONTHLY,
                                byweekday=MO,
                                byweekno=[x for x in range(1, 52, 4)],
                                dtstart=parse("20230201T090000"),
                                until=parse("20230228T090000"),
                            )
                        )
                    )
                    # TODO use parameters from shift
                    occurences = list(
                        rrule(
                            MONTHLY,
                            byweekday=MO,
                            byweekno=[x for x in range(1, 52, 4)],
                            dtstart=parse("20230201T090000"),
                            until=parse("20230228T090000"),
                        )
                    )

                    print("occurence date", occurences[0].date())
                    # 2. create virtual shift for each occurrence
                    shift.starting_shift_date = occurences[0].date()
                    print("query?", shift)
                    print("shift date NOW", shift.starting_shift_date)
                    print("queryset", queryset)
                    # 3. Append virtual shift to queryset
                    # TODO add shift with correct date instead of old shift
                    queryset = queryset | models.Shift.objects.filter(
                        pk=shift.pk,
                    )
                    print("querysetNOW", queryset)
                # 4. Append neq queryset to serializer with new queryset
                serializer_class = serializers.ShiftSerializer(
                    queryset,
                    many=True,
                )

        return Response(serializer_class.data)


class AssignmentViewSet(viewsets.ModelViewSet):
    """Manage individual shifts."""

    queryset = models.Assignment.objects.all()
    serializer_class = serializers.AssignmentSerializer


class ShiftUserViewSet(viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftUser.objects.all()
    serializer_class = serializers.ShiftUserSerializer
