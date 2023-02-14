"""Views of the user experience module."""

from rest_framework import viewsets
from rest_framework.response import Response

from . import models, serializers


class ShiftViewSet(viewsets.ModelViewSet):
    """Manage shifts."""

    queryset = models.Shift.objects.all()
    serializer_class = serializers.ShiftSerializer
    filterset_fields = {
        "shift_title": ["exact", "contains"],
        "starting_shift_date": ["gte", "lte", "exact", "gt", "lt"],
        "ending_shift_date": ["gte", "lte", "exact", "gt", "lt"],
        "shift_type": ["exact"],
        "shift_week": ["exact"],
        "shift_starting_time": ["gte", "lte", "exact", "gt", "lt"],
        "shift_ending_time": ["gte", "lte", "exact", "gt", "lt"],
        "required_users": ["gte", "lte", "exact", "gt", "lt"],
        "shift_day": ["exact"],
        "additional_info_general": ["exact", "contains"],
    }

    # list(rrule(MONTHLY, byweekday=MO(1),
    # until=NOW+relativedelta(years=+2), dtstart=NOW))

    def list(self, request):
        """List all shifts."""
        # key_list = []
        # if request.query_params:
        #     for key, value in request.query_params.items():
        #         key_list.append(key)
        #     print("keylist", key_list)

        # for shift in self.queryset:
        #     if shift.shift_type == "once":
        #         print("shift", shift.id, shift.shift_title, shift.shift_type)

        # Step 1: Select shifts with starting date <
        # request.query_params["first_shift_date__gte"]

        response = []
        for shift in self.queryset:
            # if-clause to check if shift has an ending date
            if shift.ending_shift_date:
                # if-clause to check if shift is in range
                if (
                    shift.starting_shift_date
                    >= request.query_params["first_shift_date__gte"]
                    and shift.starting_shift_date
                    <= request.query_params["ending_shift_date__lte"]
                ):
                    if shift.shift_type == "unique":
                        # if shift is unique and in range, append to response
                        response.append(shift)
                        print("Appended unique response", response)
                    elif shift.shift_type == "regular":
                        # if shift is regular and in range,
                        # add virtual shifts within range
                        # TODO: add virtual shifts
                        pass
                    else:
                        # if shift is neither unique nor regular, raise error
                        raise ValueError(
                            "Shift type must be either unique or regular.",
                        )
            else:
                # if shift has no ending date,
                # it has to be a regular shift with an open ending
                # TODO add virtual shifts within range
                pass

                response.append(shift)
        print("queryset", self.queryset[0])
        print("serializer_class", self.serializer_class)
        for key, value in request.query_params.items():
            print("request para", key, value)

        print("request", request.query_params)
        self.serializer_class = serializers.ShiftSerializer(
            self.queryset,
            many=True,
        )
        return Response(self.serializer_class.data)


class AssignmentViewSet(viewsets.ModelViewSet):
    """Manage individual shifts."""

    queryset = models.Assignment.objects.all()
    serializer_class = serializers.AssignmentSerializer


class ShiftUserViewSet(viewsets.ModelViewSet):
    """Manage shift users."""

    queryset = models.ShiftUser.objects.all()
    serializer_class = serializers.ShiftUserSerializer
