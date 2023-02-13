"""Views of the user experience module."""

from rest_framework import viewsets
from rest_framework.response import Response

from . import models, serializers


class GeneralShiftViewSet(viewsets.ModelViewSet):
    """Manage general shifts."""

    queryset = models.GeneralShift.objects.all()
    serializer_class = serializers.GeneralShiftSerializer
    filterset_fields = {
        "shift_title": ["exact"],
        "first_shift_date": ["gte", "lte", "exact", "gt", "lt"],
        "shift_type": ["exact"],
        "shift_week": ["exact"],
        "starting_date_time": ["gte"],
        "duration": ["exact"],
        "end_date_time": ["lte"],
        "required_users": ["exact"],
        "shift_day": ["exact"],
        "additional_info_general": ["exact"],
    }

    # list(rrule(MONTHLY, byweekday=MO(1),
    # until=NOW+relativedelta(years=+2), dtstart=NOW))

    def list(self, request):
        """List all general shifts."""
        # key_list = []
        # if request.query_params:
        #     for key, value in request.query_params.items():
        #         key_list.append(key)
        #     print("keylist", key_list)

        # for shift in self.queryset:
        #     if shift.shift_type == "once":
        #         print("shift", shift.id, shift.shift_title, shift.shift_type)

        print("queryset", self.queryset[0])
        print("serializer_class", self.serializer_class)
        for key, value in request.query_params.items():
            print("request para", key, value)

        print("request", request.query_params)
        self.serializer_class = serializers.GeneralShiftSerializer(
            self.queryset, many=True
        )
        return Response(self.serializer_class.data)


class IndividualShiftViewSet(viewsets.ModelViewSet):
    """Manage individual shifts."""

    queryset = models.IndividualShift.objects.all()
    serializer_class = serializers.IndividualShiftSerializer


class ShiftUserViewSet(viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftUser.objects.all()
    serializer_class = serializers.ShiftUserSerializer
