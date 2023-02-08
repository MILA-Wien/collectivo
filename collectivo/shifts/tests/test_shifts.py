"""Test the features of the shifts API."""
from django.test import TestCase
from django.urls import reverse

from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo

from ..models import GeneralShift, IndividualShift, ShiftUser

GENERAL_SHIFTS_URL = reverse("collectivo:collectivo.shifts:general-shift-list")
INDI_SHIFTS_URL = reverse("collectivo:collectivo.shifts:individual-shift-list")
SHIFT_USERS_URL = reverse("collectivo:collectivo.shifts:shift-user-list")

TEST_GENERAL_SHIFT_POST = {
    "shift_title": "my_shift",
    "first_shift_date": "2023-02-07",
    "shift_type": "fixed",
    "shift_week": "A",
    "starting_date_time": "2023-02-07T09:33:16.836Z",
    "duration": 0,
    "end_date_time": "2023-02-07T09:33:16.836Z",
    "required_users": 4,
    "shift_day": "Monday",
    "additional_info_general": "string",
}


class ShiftAPITests(TestCase):
    """Test the shifts API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(UserInfo(is_authenticated=True))
        ShiftUser.objects.create(username="Pizza")
        ShiftUser.objects.create(username="Pasta")
        ShiftUser.objects.create(username="Leone")

    def create_general_shift(self, payload=TEST_GENERAL_SHIFT_POST):
        """Create a sample member."""
        res = self.client.post(GENERAL_SHIFTS_URL, payload)
        if res.status_code != 201:
            raise ValueError("Could not register shift:", res.content)
        shift = GeneralShift.objects.get(id=res.data["id"])
        return shift

    def test_create_general_shift(self):
        """Test creating a general shift."""
        shift = self.create_general_shift()
        self.assertEqual(shift.shift_title, "my_shift")
        self.assertEqual(shift.shift_day, "Monday")

    def test_amount_of_individual_shifts_based_on_required_users(self):
        """
        Test creating a general shift.

        Test that individual shifts are created based
        on the required users attribute in general shifts.
        """
        shift = self.create_general_shift()
        self.assertEqual(
            IndividualShift.objects.filter(
                general_shift__shift_title="my_shift"
            ).count(),
            shift.required_users,
        )
        self.assertEqual(
            IndividualShift.objects.filter(
                general_shift__shift_title="my_shift"
            ).count(),
            4,
        )
        individual_shifts = IndividualShift.objects.all()
        self.assertEqual(individual_shifts[0].attended, False)
        self.assertEqual(individual_shifts[3].additional_info_individual, "")

    def test_individual_shift_gets_attributes_from_general_shift(self):
        """Test that individual shifts get atttributes from general shifts."""
        general_shift = self.create_general_shift()
        individual_shifts = IndividualShift.objects.all()
        self.assertEqual(
            general_shift.shift_title,
            individual_shifts[0].general_shift.shift_title,
        )
        self.assertEqual(
            general_shift.shift_type,
            individual_shifts[2].general_shift.shift_type,
        )

    def test_individual_shifts_is_assigned_by_user(self):
        """Test that individual shifts gets assigned by user."""
        self.create_general_shift()
        # individual_shifts = IndividualShift.objects.all()
        shift = IndividualShift.objects.all()[0]

        shift.assigned_user = ShiftUser.objects.all()[0]
        shift.save()

        self.assertEqual(
            shift.assigned_user.username,
            "Pizza",
        )
        self.assertEqual(
            shift.assigned_user.username,
            ShiftUser.objects.all()[0].username,
        )

        shift.assigned_user = ShiftUser.objects.all()[2]
        shift.save()

        self.assertEqual(
            shift.assigned_user.username,
            "Leone",
        )
        self.assertEqual(
            shift.assigned_user.username,
            ShiftUser.objects.all()[2].username,
        )

        shift.assigned_user = None
        shift.save()

        self.assertEqual(
            shift.assigned_user,
            None,
        )
