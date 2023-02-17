"""Test the features of the shifts API."""
from django.test import TestCase
from django.urls import reverse

from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.shifts.models import Assignment, Shift, ShiftUser

SHIFTS_URL = reverse("collectivo:collectivo.shifts:shift-list")
ASSIGNMENT_URL = reverse("collectivo:collectivo.shifts:assignment-list")
ASSIGNMENT_URL_LABEL = "collectivo:collectivo.shifts:assignment-detail"

SHIFT_USERS_URL = reverse("collectivo:collectivo.shifts:shift-user-list")

TEST_SHIFT_POST = {
    "shift_title": "first_regular_shift",
    "starting_shift_date": "2023-02-10",
    "ending_shift_date": "",
    "shift_type": "regular",
    "shift_week": "A",
    "shift_starting_time": "",
    "shift_ending_time": "",
    "required_users": 4,
    "shift_day": "Monday",
    "additional_info_general": "first_string",
}
TEST_SHIFT_POST2 = {
    "shift_title": "first_unique_shift",
    "starting_shift_date": "2023-02-07",
    "ending_shift_date": "",
    "shift_type": "unique",
    "shift_week": "",
    "shift_starting_time": "",
    "shift_ending_time": "",
    "required_users": 4,
    "shift_day": "Tuesday",
    "additional_info_general": "string",
}
TEST_SHIFT_POST3 = {
    "shift_title": "second_regular_shift",
    "starting_shift_date": "2023-01-01",
    "ending_shift_date": "2023-10-15",
    "shift_type": "regular",
    "shift_week": "A",
    "shift_starting_time": "",
    "shift_end_time": "",
    "required_users": 4,
    "shift_day": "Monday",
    "additional_info_general": "string",
}

TEST_CREATE_USER_POST = {"username": "Pizza", "creator": True}
TEST_CREATE_USER_POST2 = {"username": "Pasta"}


class ShiftAPITests(TestCase):
    """Test the shifts API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(UserInfo(is_authenticated=True))

    def create_shift(self, payload):
        """Create a sample member."""
        res = self.client.post(SHIFTS_URL, payload)
        if res.status_code != 201:
            raise ValueError("Could not register shift:", res.content)
        shift = Shift.objects.get(id=res.data["id"])
        return shift

    def create_shift_user(self, payload):
        """Create a sample member."""
        res = self.client.post(SHIFT_USERS_URL, payload)
        if res.status_code != 201:
            raise ValueError("Could not register shift user:", res.content)
        shift_user = ShiftUser.objects.get(id=res.data["id"])
        return shift_user

    def test_create_shift(self):
        """Test creating a shift."""
        shift = self.create_shift(payload=TEST_SHIFT_POST)
        self.assertEqual(shift.shift_title, "first_regular_shift")
        self.assertEqual(shift.shift_day, "Monday")

    def test_amount_of_assignments_based_on_required_users(self):
        """
        Test creating a shift.

        Test that assignments are created based
        on the required users attribute in shifts.
        """
        shift = self.create_shift(payload=TEST_SHIFT_POST)
        self.assertEqual(
            Assignment.objects.filter(
                shift__shift_title="first_regular_shift",
            ).count(),
            shift.required_users,
        )
        self.assertEqual(
            Assignment.objects.filter(
                shift__shift_title="first_regular_shift",
            ).count(),
            4,
        )
        assignments = Assignment.objects.all()
        self.assertEqual(assignments[0].attended, False)
        self.assertEqual(assignments[3].additional_info_individual, "")

    def test_assignment_gets_attributes_from_shift(self):
        """Test that assignments get atttributes from shifts."""
        shift = self.create_shift(payload=TEST_SHIFT_POST)
        assignments = Assignment.objects.all()
        self.assertEqual(
            shift.shift_title,
            assignments[0].shift.shift_title,
        )
        self.assertEqual(
            shift.shift_type,
            assignments[2].shift.shift_type,
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
            reverse(ASSIGNMENT_URL_LABEL, args=[shift_id]),
            payload,
        )
        if res.status_code != 200:
            raise ValueError(
                "API patch call failed, could not assign user to shift:",
                res.content,
            )
        assignment = Assignment.objects.get(id=res.data["id"])
        return assignment

    def test_assignment_is_assigned_by_user(self):
        """Test that assignments gets assigned by user."""
        # Initialize shift and users
        shift = self.create_shift(payload=TEST_SHIFT_POST)
        user = self.create_shift_user(payload=TEST_CREATE_USER_POST)
        user2 = self.create_shift_user(payload=TEST_CREATE_USER_POST2)
        assignment = shift.assignment_set.all()[0]

        # Test successful assignment
        assignment = self.assign_user_to_shift(assignment.id, user.id)
        self.assertEqual(assignment.assigned_user, user)
        self.assertEqual(
            assignment.assigned_user.username,
            "Pizza",
        )

        # Test successful unassignment
        assignment = self.assign_user_to_shift(assignment.id, None)
        self.assertEqual(assignment.assigned_user, None)

        # Test successful reassignment
        assignment = self.assign_user_to_shift(assignment.id, user2.id)
        self.assertEqual(assignment.assigned_user, user2)
        self.assertEqual(
            assignment.assigned_user.username,
            "Pasta",
        )

    def test_to_filter_no_shifts(self):
        """Test to filter no shifts by using weird params."""
        self.create_shift(payload=TEST_SHIFT_POST)
        self.create_shift(payload=TEST_SHIFT_POST2)
        self.create_shift(payload=TEST_SHIFT_POST3)

        res = self.client.get(
            SHIFTS_URL
            + "?shift_type=regular&"
            + "shift_week=Q&"
            + "additional_info_general=weird"
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_to_filter_shifts_without_starting_shift_date_as_param(self):
        """Test to filter shifts without using param starting_shift_date."""
        self.create_shift(payload=TEST_SHIFT_POST)
        self.create_shift(payload=TEST_SHIFT_POST2)
        self.create_shift(payload=TEST_SHIFT_POST3)

        res = self.client.get(
            SHIFTS_URL
            + "?shift_type=regular&"
            + "shift_week=A&"
            + "additional_info_general=string"
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["shift_title"], "second_regular_shift")

    def test_to_filter_unique_shifts(self):
        """Test to filter unique shifts."""
        self.create_shift(payload=TEST_SHIFT_POST)
        self.create_shift(payload=TEST_SHIFT_POST2)
        self.create_shift(payload=TEST_SHIFT_POST3)

        res = self.client.get(
            SHIFTS_URL
            + "?starting_shift_date__gte=2023-02-01&"
            + "starting_shift_date__lte=2023-02-28&"
            + "shift_type=unique"
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["shift_title"], "first_unique_shift")

    def test_to_filter_regular_shifts(self):
        """Test only one shift is returned due to filters."""
        self.create_shift(payload=TEST_SHIFT_POST)
        self.create_shift(payload=TEST_SHIFT_POST2)
        self.create_shift(payload=TEST_SHIFT_POST3)

        res = self.client.get(
            SHIFTS_URL
            + "?starting_shift_date__gte=2023-02-01&"
            + "starting_shift_date__lte=2023-02-28&"
            + "shift_type=regular&"
            + "additional_info_general=first_string"
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["shift_title"], "first_regular_shift")

    def test_to_filter_virtually_created_regular_shifts(self):
        """Test virutally creating shifts.

        Even though one shift is out of bounds of specified date range.
        """
        self.create_shift(payload=TEST_SHIFT_POST)
        self.create_shift(payload=TEST_SHIFT_POST2)
        self.create_shift(payload=TEST_SHIFT_POST3)

        res = self.client.get(
            SHIFTS_URL
            + "?starting_shift_date__gte=2023-02-01&"
            + "starting_shift_date__lte=2023-02-28"
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 3)
        self.assertEqual(res.data[0]["shift_title"], "first_regular_shift")
        self.assertEqual(res.data[1]["shift_title"], "first_unique_shift")
        self.assertEqual(res.data[2]["shift_title"], "second_regular_shift")

    def test_creating_two_shifts_with_same_id(self):
        """Test creating two shifts with same id.

        Due to possibility of two occurences of same shift in a month.
        """
        self.create_shift(payload=TEST_SHIFT_POST)
        self.create_shift(payload=TEST_SHIFT_POST2)
        self.create_shift(payload=TEST_SHIFT_POST3)

        res = self.client.get(
            SHIFTS_URL
            + "?starting_shift_date__gte=2023-01-01&"
            + "starting_shift_date__lte=2023-01-31"
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data[1]["starting_shift_date"], "2023-01-02")
        self.assertEqual(len(res.data), 3)

    # def test_to_filter_regular_shifts_ending_within_date_range(self):
    #     """Test that multiple shifts can be retrieved."""
    #     self.create_shift(payload=TEST_SHIFT_POST)
    #     self.create_shift(payload=TEST_SHIFT_POST2)
    #     self.create_shift(payload=TEST_SHIFT_POST3)

    #     res = self.client.get(
    #         SHIFTS_URL
    #         + "?starting_shift_date__gte=2023-02-01&"
    #         + "starting_shift_date__lte=2023-02-28"
    #     )

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(len(res.data), 3)
    #     self.assertEqual(res.data[2]["shift_title"], "second_regular_shift")
