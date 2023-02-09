"""Test the features of the shifts API."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.shifts.models import GeneralShift, IndividualShift, ShiftUser
from collectivo.shifts.serializers import IndividualShiftSerializer

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

TEST_CREATE_USER_POST = {"username": "Pizza", "creator": True}
TEST_CREATE_USER_POST2 = {"username": "Pasta"}
TEST_CREATE_USER_POST3 = {"username": "Leone"}

TEST_ASSIGN_POST = {"additional_info_individual": "string", "assigned_user": 1}


class ShiftAPITests(TestCase):
    """Test the shifts API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(UserInfo(is_authenticated=True))

    def create_general_shift(self, payload=TEST_GENERAL_SHIFT_POST):
        """Create a sample member."""
        res = self.client.post(GENERAL_SHIFTS_URL, payload)
        if res.status_code != 201:
            raise ValueError("Could not register shift:", res.content)
        shift = GeneralShift.objects.get(id=res.data["id"])
        return shift

    def create_shift_user(self, payload=TEST_CREATE_USER_POST):
        """Create a sample member."""
        res = self.client.post(SHIFT_USERS_URL, payload)
        if res.status_code != 201:
            raise ValueError("Could not register shift user:", res.content)
        shift_user = ShiftUser.objects.get(id=res.data["id"])
        return shift_user

    def create_shift_user2(self, payload=TEST_CREATE_USER_POST2):
        """Create a sample member."""
        res = self.client.post(SHIFT_USERS_URL, payload)
        if res.status_code != 201:
            raise ValueError("Could not register shift user:", res.content)
        shift_user = ShiftUser.objects.get(id=res.data["id"])
        return shift_user

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

    def assign_user_to_shift(self, shift_id, user_id, payload=TEST_ASSIGN_POST):
        """Assign user to shift."""
        print("payload", payload)
        res = self.client.patch(INDI_SHIFTS_URL + str(shift_id) + "/", payload)
        if res.status_code != 200:
            raise ValueError("Could not assign user to shift:", res.content)
        shift = IndividualShift.objects.get(id=res.data["id"])
        print(
            "shift in assign user to shift",
            shift.id,
            shift.assigned_user,
            shift.additional_info_individual,
        )
        return shift

    def test_individual_shifts_is_assigned_by_user(self):
        """Test that individual shifts gets assigned by user."""
        self.create_general_shift()
        self.create_shift_user()
        self.create_shift_user2()
        shift = IndividualShift.objects.all()[0]
        print("shift", shift.id, shift.assigned_user, shift.general_shift.id)
        user = ShiftUser.objects.all()[0]
        print("user", user.id, user.username)
        user2 = ShiftUser.objects.all()[1]
        serializer = IndividualShiftSerializer()
        print("URL", INDI_SHIFTS_URL + str(shift.id) + "/")

        # Test successful assignment
        # serializer.assign_user(user, shift)
        # self.client.patch({"assigned_user": user.id}, shift.id)
        shift = self.assign_user_to_shift(shift.id, user.id)
        print(
            "after", shift.id, shift.additional_info_individual, shift.general_shift.id
        )
        self.assertEqual(shift.assigned_user, user)

        self.assertEqual(
            shift.assigned_user.username,
            "Pizza",
        )

        # Test error raised for already assigned shift
        with self.assertRaises(ValidationError):
            serializer.assign_user(user, shift)

        # Test successful unassignment
        serializer.assign_user(None, shift)
        self.assertEqual(shift.assigned_user, None)

        # Test successful reassignment
        serializer.assign_user(user2, shift)
        self.assertEqual(shift.assigned_user, user2)
