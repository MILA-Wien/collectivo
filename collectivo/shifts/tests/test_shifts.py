"""Test the features of the shifts API."""
from django.test import TestCase
from django.urls import reverse

from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.shifts.models import GeneralShift, IndividualShift, ShiftUser

GENERAL_SHIFTS_URL = reverse("collectivo:collectivo.shifts:general-shift-list")
INDI_SHIFTS_URL = reverse("collectivo:collectivo.shifts:individual-shift-list")
INDI_SHIFTS_URL_LABEL = "collectivo:collectivo.shifts:individual-shift-detail"

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

    def assign_user_to_shift(self, shift_id, user_id=None):
        """Assign user to shift."""
        if user_id is None:
            payload = {
                "additional_info_individual": "string",
                "assigned_user": "",
            }
        else:
            payload = {
                "additional_info_individual": "string",
                "assigned_user": user_id,
            }

        res = self.client.patch(
            reverse(INDI_SHIFTS_URL_LABEL, args=[shift_id]), payload
        )
        if res.status_code != 200:
            raise ValueError(
                "API patch call failed, could not assign user to shift:",
                res.content,
            )
        indi_shift = IndividualShift.objects.get(id=res.data["id"])
        return indi_shift

    def test_individual_shifts_is_assigned_by_user(self):
        """Test that individual shifts gets assigned by user."""
        # Initialize shift and use
        shift = self.create_general_shift()
        user = self.create_shift_user()
        user2 = self.create_shift_user2()
        indi_shift = shift.individualshift_set.all()[0]

        # Test successful assignment
        indi_shift = self.assign_user_to_shift(indi_shift.id, user.id)
        self.assertEqual(indi_shift.assigned_user, user)
        self.assertEqual(
            indi_shift.assigned_user.username,
            "Pizza",
        )

        # Test successful unassignment
        indi_shift = self.assign_user_to_shift(indi_shift.id, None)
        self.assertEqual(indi_shift.assigned_user, None)

        # Test successful reassignment
        indi_shift = self.assign_user_to_shift(indi_shift.id, user2.id)
        self.assertEqual(indi_shift.assigned_user, user2)
        self.assertEqual(
            indi_shift.assigned_user.username,
            "Pasta",
        )
