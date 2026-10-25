from datetime import date, datetime
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from chores.models import Household, Membership, Chore, ChoreCompletion


class SmokeTest(TestCase):
    """Smoke test — confirms the app boots and the home route responds."""

    def test_home_returns_200(self):
        response = self.client.get(reverse("chores:index"))
        self.assertLess(response.status_code, 500)


class SanityTest(TestCase):
    """Plain unit test — no Django at all."""

    def test_addition(self):
        self.assertEqual(1 + 1, 2)


class RegisterViewTest(TestCase):
    """Tests for GET/POST /register/."""

    def test_get_register_renders_form(self):
        """GET /register/ returns 200 and contains a form."""
        response = self.client.get(reverse("chores:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")

    def test_valid_registration_creates_user_and_redirects(self):
        """POST with valid data creates a User, logs the user in, and redirects to /dashboard/."""
        response = self.client.post(
            reverse("chores:register"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        # Redirects to dashboard
        self.assertRedirects(response, reverse("chores:dashboard"))
        # User was created
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # User is logged in (session has _auth_user_id)
        self.assertIn("_auth_user_id", self.client.session)

    def test_invalid_registration_rerenders_with_errors(self):
        """POST with mismatched passwords re-renders the form with errors."""
        response = self.client.post(
            reverse("chores:register"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "WrongPass999!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())
        # Form errors are present
        self.assertContains(response, "error")


class LoginViewTest(TestCase):
    """Tests for GET/POST /login/."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")

    def test_get_login_renders_form(self):
        """GET /login/ returns 200 and contains a form."""
        response = self.client.get(reverse("chores:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")

    def test_valid_login_redirects_to_dashboard(self):
        """POST with valid credentials logs in and redirects to /dashboard/."""
        response = self.client.post(
            reverse("chores:login"),
            {"username": "testuser", "password": "TestPass123!"},
        )
        self.assertRedirects(response, reverse("chores:dashboard"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_invalid_login_rerenders_with_error(self):
        """POST with wrong password re-renders the form with an error."""
        response = self.client.post(
            reverse("chores:login"),
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_honours_next_parameter(self):
        """POST /login/?next=/some-url/ redirects to that URL after login."""
        response = self.client.post(
            reverse("chores:login") + "?next=/dashboard/",
            {"username": "testuser", "password": "TestPass123!"},
        )
        self.assertRedirects(response, "/dashboard/")


class LogoutViewTest(TestCase):
    """Tests for POST /logout/."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")

    def test_logout_redirects_to_login(self):
        """POST /logout/ logs out the user and redirects to /login/."""
        self.client.login(username="testuser", password="TestPass123!")
        response = self.client.post(reverse("chores:logout"))
        self.assertRedirects(response, reverse("chores:login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class DashboardViewTest(TestCase):
    """Tests for GET /dashboard/."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")

    def test_dashboard_requires_login(self):
        """Anonymous users are redirected to /login/ when accessing /dashboard/."""
        response = self.client.get(reverse("chores:dashboard"))
        self.assertRedirects(response, "/login/?next=/dashboard/")

    def test_dashboard_accessible_when_logged_in(self):
        """Authenticated users can access /dashboard/ and see their username."""
        self.client.login(username="testuser", password="TestPass123!")
        response = self.client.get(reverse("chores:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")


class HouseholdModelTest(TestCase):
    """Tests for the Household model."""

    def setUp(self):
        self.user = User.objects.create_user(username="owner1", password="Password123!")

    def test_invite_code_is_auto_populated_on_save(self):
        """invite_code is generated automatically on save and is not empty."""
        household = Household.objects.create(name="Smith Family", owner=self.user)
        self.assertTrue(household.invite_code)
        self.assertGreater(len(household.invite_code), 5)

    def test_two_saves_dont_overwrite_existing_invite_code(self):
        """Saving an existing household retains its original invite_code."""
        household = Household.objects.create(name="Smith Family", owner=self.user)
        code1 = household.invite_code
        household.name = "Smith Household Updated"
        household.save()
        self.assertEqual(household.invite_code, code1)

    def test_owner_is_implicit_member(self):
        """Owner is returned by get_members even if no Membership row exists."""
        household = Household.objects.create(name="Smith Family", owner=self.user)
        # Verify no explicit Membership row exists
        self.assertEqual(household.memberships.count(), 0)
        # get_members still includes owner
        members = household.get_members()
        self.assertIn(self.user, members)


class CreateHouseholdViewTest(TestCase):
    """Tests for GET/POST /households/create/."""

    def setUp(self):
        self.user = User.objects.create_user(username="owner1", password="Password123!")

    def test_anonymous_redirected_to_login(self):
        """Anonymous users attempting to create a household are redirected to login."""
        response = self.client.get(reverse("chores:create_household"))
        self.assertRedirects(response, "/login/?next=/households/create/")

    def test_owner_can_create_household_and_redirects(self):
        """Logged-in user can submit create-household form and is redirected to detail."""
        self.client.login(username="owner1", password="Password123!")
        response = self.client.post(
            reverse("chores:create_household"),
            {"name": "Baker Street House"},
        )
        household = Household.objects.get(name="Baker Street House")
        self.assertEqual(household.owner, self.user)
        self.assertRedirects(response, reverse("chores:household_detail", kwargs={"pk": household.pk}))

    def test_owner_blocked_from_creating_second_household(self):
        """User who already owns a household cannot create another."""
        Household.objects.create(name="First House", owner=self.user)
        self.client.login(username="owner1", password="Password123!")
        response = self.client.post(
            reverse("chores:create_household"),
            {"name": "Second House"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You already own a household.")
        self.assertEqual(Household.objects.filter(owner=self.user).count(), 1)


class HouseholdDetailViewTest(TestCase):
    """Tests for GET /households/<pk>/."""

    def setUp(self):
        self.user = User.objects.create_user(username="owner1", password="Password123!")
        self.household = Household.objects.create(name="Smith Family", owner=self.user)

    def test_anonymous_redirected_to_login(self):
        """Anonymous users are redirected to login."""
        response = self.client.get(reverse("chores:household_detail", kwargs={"pk": self.household.pk}))
        self.assertRedirects(response, f"/login/?next=/households/{self.household.pk}/")

    def test_detail_page_shows_name_and_invite_code(self):
        """Logged-in user sees household name, owner, and invite code."""
        self.client.login(username="owner1", password="Password123!")
        response = self.client.get(reverse("chores:household_detail", kwargs={"pk": self.household.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.household.name)
        self.assertContains(response, self.household.invite_code)
        self.assertContains(response, self.user.username)


class JoinHouseholdViewTest(TestCase):
    """Tests for GET/POST /join/."""

    def setUp(self):
        self.owner = User.objects.create_user(username="owner1", password="Password123!")
        self.household = Household.objects.create(name="Smith Family", owner=self.owner)
        self.member_user = User.objects.create_user(username="member1", password="Password123!")

    def test_anonymous_redirected_to_login(self):
        """Anonymous user attempting to join is redirected to login."""
        response = self.client.get(reverse("chores:join_household"))
        self.assertRedirects(response, "/login/?next=/join/")

    def test_valid_code_creates_membership_row(self):
        """Valid invite code creates a Membership row and redirects to household detail."""
        self.client.login(username="member1", password="Password123!")
        response = self.client.post(
            reverse("chores:join_household"),
            {"invite_code": self.household.invite_code},
        )
        self.assertRedirects(response, reverse("chores:household_detail", kwargs={"pk": self.household.pk}))
        self.assertTrue(
            Membership.objects.filter(household=self.household, user=self.member_user).exists()
        )
        # Check get_members includes newly joined user
        self.assertIn(self.member_user, self.household.get_members())

    def test_invalid_code_shows_form_error(self):
        """Invalid invite code displays an error and creates no Membership row."""
        self.client.login(username="member1", password="Password123!")
        response = self.client.post(
            reverse("chores:join_household"),
            {"invite_code": "NON_EXISTENT_CODE"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid invite code.")
        self.assertFalse(Membership.objects.filter(user=self.member_user).exists())

    def test_already_a_member_shows_form_error(self):
        """User already a member of the household cannot join again."""
        Membership.objects.create(household=self.household, user=self.member_user)
        self.client.login(username="member1", password="Password123!")
        response = self.client.post(
            reverse("chores:join_household"),
            {"invite_code": self.household.invite_code},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are already a member of this household.")
        self.assertEqual(Membership.objects.filter(household=self.household, user=self.member_user).count(), 1)

    def test_user_already_in_another_household_is_rejected(self):
        """User already belonging to a different household cannot join a new one."""
        other_owner = User.objects.create_user(username="other_owner", password="Password123!")
        other_household = Household.objects.create(name="Jones Family", owner=other_owner)
        Membership.objects.create(household=other_household, user=self.member_user)

        self.client.login(username="member1", password="Password123!")
        response = self.client.post(
            reverse("chores:join_household"),
            {"invite_code": self.household.invite_code},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You already belong to another household.")
        self.assertFalse(Membership.objects.filter(household=self.household, user=self.member_user).exists())


class ChoreModelTest(TestCase):
    """Tests for the Chore model validation and defaults."""

    def setUp(self):
        self.owner = User.objects.create_user(username="owner1", password="Password123!")
        self.household = Household.objects.create(name="Smith Family", owner=self.owner)

    def test_point_value_zero_raises_validation_error(self):
        """point_value = 0 fails validation."""
        chore = Chore(
            household=self.household,
            title="Clean Kitchen",
            frequency=Chore.Frequency.DAILY,
            point_value=0,
            next_due_date=date.today(),
        )
        with self.assertRaises(ValidationError):
            chore.full_clean()

    def test_point_value_negative_raises_validation_error(self):
        """point_value = -1 fails validation."""
        chore = Chore(
            household=self.household,
            title="Clean Kitchen",
            frequency=Chore.Frequency.DAILY,
            point_value=-1,
            next_due_date=date.today(),
        )
        with self.assertRaises(ValidationError):
            chore.full_clean()

    def test_point_value_positive_is_valid(self):
        """point_value = 1 is valid."""
        chore = Chore(
            household=self.household,
            title="Clean Kitchen",
            frequency=Chore.Frequency.DAILY,
            point_value=1,
            next_due_date=date.today(),
        )
        chore.full_clean()  # should not raise
        chore.save()
        self.assertEqual(chore.point_value, 1)

    def test_frequency_invalid_raises_validation_error(self):
        """frequency = 'monthly' fails validation."""
        chore = Chore(
            household=self.household,
            title="Clean Kitchen",
            frequency="monthly",
            point_value=5,
            next_due_date=date.today(),
        )
        with self.assertRaises(ValidationError):
            chore.full_clean()

    def test_frequency_daily_and_weekly_are_valid(self):
        """frequency = 'daily' and 'weekly' are valid."""
        daily_chore = Chore(
            household=self.household,
            title="Wash Dishes",
            frequency=Chore.Frequency.DAILY,
            point_value=10,
            next_due_date=date.today(),
        )
        daily_chore.full_clean()

        weekly_chore = Chore(
            household=self.household,
            title="Mow Lawn",
            frequency=Chore.Frequency.WEEKLY,
            point_value=25,
            next_due_date=date.today(),
        )
        weekly_chore.full_clean()

    def test_rotation_members_defaults_to_empty_list(self):
        """rotation_members defaults to an empty list."""
        chore = Chore.objects.create(
            household=self.household,
            title="Take out Trash",
            frequency=Chore.Frequency.DAILY,
            point_value=5,
            next_due_date=date.today(),
        )
        self.assertEqual(chore.rotation_members, [])

    def test_description_is_optional(self):
        """description is optional (blank is valid)."""
        chore = Chore(
            household=self.household,
            title="Take out Trash",
            description="",
            frequency=Chore.Frequency.DAILY,
            point_value=5,
            next_due_date=date.today(),
        )
        chore.full_clean()
        chore.save()
        self.assertEqual(chore.description, "")


class ChoreManagementViewTest(TestCase):
    """Tests for chore CRUD operations and permissions."""

    def setUp(self):
        self.owner = User.objects.create_user(username="owner1", password="Password123!")
        self.member = User.objects.create_user(username="member1", password="Password123!")
        self.stranger = User.objects.create_user(username="stranger", password="Password123!")
        self.household = Household.objects.create(name="Smith Family", owner=self.owner)
        Membership.objects.create(household=self.household, user=self.owner)
        Membership.objects.create(household=self.household, user=self.member)
        self.chore = Chore.objects.create(
            household=self.household,
            title="Clean Kitchen",
            frequency=Chore.Frequency.DAILY,
            point_value=10,
            next_due_date=date.today(),
            rotation_members=[self.owner.pk, self.member.pk],
        )

    def test_chore_list_shows_all_chores_for_household(self):
        """Member can access chore list and see chores."""
        self.client.login(username="member1", password="Password123!")
        response = self.client.get(reverse("chores:chore_list", kwargs={"pk": self.household.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clean Kitchen")

    def test_non_member_cannot_view_chore_list(self):
        """Non-member receives 403 on chore list."""
        self.client.login(username="stranger", password="Password123!")
        response = self.client.get(reverse("chores:chore_list", kwargs={"pk": self.household.pk}))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_create_chore(self):
        """Owner can access create form and submit valid chore."""
        self.client.login(username="owner1", password="Password123!")
        response = self.client.post(
            reverse("chores:chore_create", kwargs={"pk": self.household.pk}),
            {
                "title": "Mow Lawn",
                "description": "Front yard",
                "frequency": Chore.Frequency.WEEKLY,
                "point_value": 20,
                "next_due_date": "2026-11-01",
                "rotation_members": [str(self.owner.pk)],
            },
        )
        self.assertRedirects(response, reverse("chores:chore_list", kwargs={"pk": self.household.pk}))
        self.assertTrue(Chore.objects.filter(title="Mow Lawn", household=self.household).exists())

    def test_member_receives_403_on_create(self):
        """Household member (not owner) receives 403 on create view."""
        self.client.login(username="member1", password="Password123!")
        response = self.client.post(
            reverse("chores:chore_create", kwargs={"pk": self.household.pk}),
            {
                "title": "Mow Lawn",
                "frequency": Chore.Frequency.WEEKLY,
                "point_value": 20,
                "next_due_date": "2026-11-01",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_anonymous_redirected_to_login_on_create(self):
        """Anonymous user is redirected to login on create view."""
        response = self.client.get(reverse("chores:chore_create", kwargs={"pk": self.household.pk}))
        self.assertRedirects(response, f"/login/?next=/households/{self.household.pk}/chores/create/")

    def test_owner_can_edit_chore(self):
        """Owner can edit an existing chore."""
        self.client.login(username="owner1", password="Password123!")
        response = self.client.post(
            reverse("chores:chore_edit", kwargs={"pk": self.household.pk, "chore_pk": self.chore.pk}),
            {
                "title": "Clean Whole Kitchen",
                "description": "Including oven",
                "frequency": Chore.Frequency.DAILY,
                "point_value": 15,
                "next_due_date": "2026-11-02",
                "rotation_members": [str(self.member.pk)],
            },
        )
        self.assertRedirects(response, reverse("chores:chore_list", kwargs={"pk": self.household.pk}))
        self.chore.refresh_from_db()
        self.assertEqual(self.chore.title, "Clean Whole Kitchen")
        self.assertEqual(self.chore.point_value, 15)
        self.assertEqual(self.chore.rotation_members, [self.member.pk])

    def test_member_receives_403_on_edit(self):
        """Household member receives 403 on edit view."""
        self.client.login(username="member1", password="Password123!")
        response = self.client.post(
            reverse("chores:chore_edit", kwargs={"pk": self.household.pk, "chore_pk": self.chore.pk}),
            {"title": "Hacked Title"},
        )
        self.assertEqual(response.status_code, 403)

    def test_owner_can_delete_chore(self):
        """Owner can delete a chore via POST."""
        self.client.login(username="owner1", password="Password123!")
        response = self.client.post(
            reverse("chores:chore_delete", kwargs={"pk": self.household.pk, "chore_pk": self.chore.pk})
        )
        self.assertRedirects(response, reverse("chores:chore_list", kwargs={"pk": self.household.pk}))
        self.assertFalse(Chore.objects.filter(pk=self.chore.pk).exists())

    def test_member_receives_403_on_delete(self):
        """Household member receives 403 on delete view."""
        self.client.login(username="member1", password="Password123!")
        response = self.client.post(
            reverse("chores:chore_delete", kwargs={"pk": self.household.pk, "chore_pk": self.chore.pk})
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Chore.objects.filter(pk=self.chore.pk).exists())


class ChoreRotationLogicTest(TestCase):
    """Tests for pure rotation logic in chores/rotation.py."""

    def test_first_slot_when_not_yet_due(self):
        """When reference_date is before next_due_date, index is 0."""
        from chores.rotation import current_responsible_index
        idx = current_responsible_index(
            rotation_members=[1, 2, 3],
            next_due_date=date(2026, 11, 10),
            frequency="daily",
            reference_date=date(2026, 11, 5),
        )
        self.assertEqual(idx, 0)

    def test_first_slot_when_due_today(self):
        """When reference_date equals next_due_date, index is 0."""
        from chores.rotation import current_responsible_index
        idx = current_responsible_index(
            rotation_members=[10, 20, 30],
            next_due_date=date(2026, 11, 1),
            frequency="daily",
            reference_date=date(2026, 11, 1),
        )
        self.assertEqual(idx, 0)

    def test_second_member_one_period_elapsed_daily(self):
        """One day elapsed on daily chore advances index to 1."""
        from chores.rotation import current_responsible_index
        idx = current_responsible_index(
            rotation_members=[10, 20, 30],
            next_due_date=date(2026, 11, 1),
            frequency="daily",
            reference_date=date(2026, 11, 2),
        )
        self.assertEqual(idx, 1)

    def test_second_member_one_period_elapsed_weekly(self):
        """One week (7 days) elapsed on weekly chore advances index to 1."""
        from chores.rotation import current_responsible_index
        idx = current_responsible_index(
            rotation_members=[10, 20, 30],
            next_due_date=date(2026, 11, 1),
            frequency="weekly",
            reference_date=date(2026, 11, 8),
        )
        self.assertEqual(idx, 1)

    def test_wrap_around_back_to_first_member(self):
        """When elapsed periods equals list length, wraps around to 0."""
        from chores.rotation import current_responsible_index
        idx = current_responsible_index(
            rotation_members=[10, 20],
            next_due_date=date(2026, 11, 1),
            frequency="daily",
            reference_date=date(2026, 11, 3),  # 2 days elapsed, len=2 -> 0
        )
        self.assertEqual(idx, 0)

    def test_overdue_by_more_than_one_period(self):
        """Overdue by multiple periods wraps correctly."""
        from chores.rotation import current_responsible_index
        # 5 days elapsed on daily with 3 members: 5 % 3 = 2 -> index 2
        idx = current_responsible_index(
            rotation_members=[101, 102, 103],
            next_due_date=date(2026, 11, 1),
            frequency="daily",
            reference_date=date(2026, 11, 6),
        )
        self.assertEqual(idx, 2)

    def test_single_member_always_returns_zero(self):
        """Single-member list always returns 0 regardless of dates."""
        from chores.rotation import current_responsible_index
        idx = current_responsible_index(
            rotation_members=[42],
            next_due_date=date(2026, 1, 1),
            frequency="daily",
            reference_date=date(2026, 12, 31),
        )
        self.assertEqual(idx, 0)

    def test_empty_rotation_members_raises_value_error(self):
        """Empty rotation list raises ValueError."""
        from chores.rotation import current_responsible_index
        with self.assertRaises(ValueError):
            current_responsible_index(
                rotation_members=[],
                next_due_date=date(2026, 11, 1),
                frequency="daily",
                reference_date=date(2026, 11, 1),
            )

    def test_invalid_frequency_raises_value_error(self):
        """Invalid frequency raises ValueError."""
        from chores.rotation import current_responsible_index
        with self.assertRaises(ValueError):
            current_responsible_index(
                rotation_members=[1],
                next_due_date=date(2026, 11, 1),
                frequency="monthly",
                reference_date=date(2026, 11, 1),
            )


class BoardViewTest(TestCase):
    """Tests for GET /households/<pk>/board/."""

    def setUp(self):
        from datetime import timedelta
        self.owner = User.objects.create_user(username="owner1", password="Password123!")
        self.member = User.objects.create_user(username="member1", password="Password123!")
        self.stranger = User.objects.create_user(username="stranger", password="Password123!")
        self.household = Household.objects.create(name="Smith Family", owner=self.owner)
        Membership.objects.create(household=self.household, user=self.owner)
        Membership.objects.create(household=self.household, user=self.member)

        today = date.today()
        self.pending_chore = Chore.objects.create(
            household=self.household,
            title="Future Chore",
            frequency=Chore.Frequency.DAILY,
            point_value=10,
            next_due_date=today + timedelta(days=2),
            rotation_members=[self.member.pk],
        )
        self.overdue_chore = Chore.objects.create(
            household=self.household,
            title="Overdue Chore",
            frequency=Chore.Frequency.DAILY,
            point_value=15,
            next_due_date=today - timedelta(days=2),
            rotation_members=[self.owner.pk],
        )

    def test_member_can_access_board(self):
        """Member can access board."""
        self.client.login(username="member1", password="Password123!")
        response = self.client.get(reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertEqual(response.status_code, 200)

    def test_non_member_receives_403(self):
        """Non-member receives 403 on board view."""
        self.client.login(username="stranger", password="Password123!")
        response = self.client.get(reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_redirected_to_login(self):
        """Anonymous user is redirected to login."""
        response = self.client.get(reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertRedirects(response, f"/login/?next=/households/{self.household.pk}/board/")

    def test_board_shows_all_chores_and_statuses(self):
        """Board shows chores, responsible names, and Pending/Overdue statuses."""
        self.client.login(username="owner1", password="Password123!")
        response = self.client.get(reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Future Chore")
        self.assertContains(response, "Overdue Chore")
        self.assertContains(response, "Pending")
        self.assertContains(response, "Overdue")
        # Check responsible members
        self.assertContains(response, "member1")
        self.assertContains(response, "owner1")


class CompleteChoreViewTest(TestCase):
    """Tests for POST /households/<pk>/chores/<chore_pk>/complete/."""

    def setUp(self):
        from datetime import timedelta
        self.owner = User.objects.create_user(username="owner1", password="Password123!")
        self.member = User.objects.create_user(username="member1", password="Password123!")
        self.household = Household.objects.create(name="Smith Family", owner=self.owner)
        Membership.objects.create(household=self.household, user=self.owner)
        Membership.objects.create(household=self.household, user=self.member)

        self.today = date.today()
        # Daily chore assigned to member1
        self.daily_chore = Chore.objects.create(
            household=self.household,
            title="Clean Dishes",
            frequency=Chore.Frequency.DAILY,
            point_value=5,
            next_due_date=self.today,
            rotation_members=[self.member.pk, self.owner.pk],
        )
        # Weekly chore assigned to owner1
        self.weekly_chore = Chore.objects.create(
            household=self.household,
            title="Vacuum Living Room",
            frequency=Chore.Frequency.WEEKLY,
            point_value=15,
            next_due_date=self.today,
            rotation_members=[self.owner.pk, self.member.pk],
        )

    def test_anonymous_redirected_to_login(self):
        """Anonymous user is redirected to login."""
        response = self.client.post(
            reverse("chores:complete_chore", kwargs={"pk": self.household.pk, "chore_pk": self.daily_chore.pk})
        )
        self.assertRedirects(response, f"/login/?next=/households/{self.household.pk}/chores/{self.daily_chore.pk}/complete/")

    def test_non_assigned_member_receives_403(self):
        """Non-assigned member attempting to complete receives 403."""
        self.client.login(username="owner1", password="Password123!")
        response = self.client.post(
            reverse("chores:complete_chore", kwargs={"pk": self.household.pk, "chore_pk": self.daily_chore.pk})
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ChoreCompletion.objects.count(), 0)

    def test_assigned_member_completes_daily_chore_advances_one_day(self):
        """Assigned member completes chore: record created, next_due_date advanced by 1 day."""
        from datetime import timedelta
        self.client.login(username="member1", password="Password123!")
        response = self.client.post(
            reverse("chores:complete_chore", kwargs={"pk": self.household.pk, "chore_pk": self.daily_chore.pk})
        )
        self.assertRedirects(response, reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertEqual(ChoreCompletion.objects.count(), 1)
        completion = ChoreCompletion.objects.first()
        self.assertEqual(completion.chore, self.daily_chore)
        self.assertEqual(completion.completed_by, self.member)
        self.assertFalse(completion.verified)

        self.daily_chore.refresh_from_db()
        self.assertEqual(self.daily_chore.next_due_date, self.today + timedelta(days=1))

    def test_assigned_member_completes_weekly_chore_advances_seven_days(self):
        """Assigned member completes weekly chore: next_due_date advanced by 7 days."""
        from datetime import timedelta
        self.client.login(username="owner1", password="Password123!")
        response = self.client.post(
            reverse("chores:complete_chore", kwargs={"pk": self.household.pk, "chore_pk": self.weekly_chore.pk})
        )
        self.assertRedirects(response, reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.weekly_chore.refresh_from_db()
        self.assertEqual(self.weekly_chore.next_due_date, self.today + timedelta(weeks=1))

    def test_duplicate_completion_in_same_period_is_rejected(self):
        """Attempting duplicate completion in the same period is rejected."""
        self.client.login(username="member1", password="Password123!")
        # First completion
        self.client.post(
            reverse("chores:complete_chore", kwargs={"pk": self.household.pk, "chore_pk": self.daily_chore.pk})
        )
        self.assertEqual(ChoreCompletion.objects.count(), 1)

        # Attempt duplicate completion (now next_due_date is advanced, status is Done for today)
        response = self.client.post(
            reverse("chores:complete_chore", kwargs={"pk": self.household.pk, "chore_pk": self.daily_chore.pk})
        )
        # Should be rejected with 400 or 403 (or bad request) and count remains 1
        self.assertIn(response.status_code, [400, 403])
        self.assertEqual(ChoreCompletion.objects.count(), 1)

    def test_board_shows_mark_complete_only_to_assigned_member(self):
        """Board HTML contains Mark Complete button only for the assigned member."""
        # Logged in as member1 (assigned to daily_chore)
        self.client.login(username="member1", password="Password123!")
        response = self.client.get(reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"/chores/{self.daily_chore.pk}/complete/")
        # Does not have button for weekly_chore (assigned to owner1)
        self.assertNotContains(response, f"/chores/{self.weekly_chore.pk}/complete/")


class VerifyCompletionViewTest(TestCase):
    """Tests for POST /households/<pk>/completions/<completion_pk>/verify/."""

    def setUp(self):
        from datetime import timedelta
        self.owner = User.objects.create_user(username="owner1", password="Password123!")
        self.member = User.objects.create_user(username="member1", password="Password123!")
        self.stranger = User.objects.create_user(username="stranger", password="Password123!")
        self.household = Household.objects.create(name="Smith Family", owner=self.owner)
        Membership.objects.create(household=self.household, user=self.owner)
        Membership.objects.create(household=self.household, user=self.member)

        today = date.today()
        self.chore = Chore.objects.create(
            household=self.household,
            title="Clean Kitchen",
            frequency=Chore.Frequency.DAILY,
            point_value=10,
            next_due_date=today + timedelta(days=1),
            rotation_members=[self.member.pk, self.owner.pk],
        )
        self.completion = ChoreCompletion.objects.create(
            chore=self.chore,
            completed_by=self.member,
            verified=False,
        )

    def test_anonymous_redirected_to_login(self):
        """Anonymous user is redirected to login."""
        response = self.client.post(
            reverse("chores:verify_completion", kwargs={"pk": self.household.pk, "completion_pk": self.completion.pk})
        )
        self.assertRedirects(response, f"/login/?next=/households/{self.household.pk}/completions/{self.completion.pk}/verify/")

    def test_non_member_receives_403(self):
        """Non-member receives 403 on verify."""
        self.client.login(username="stranger", password="Password123!")
        response = self.client.post(
            reverse("chores:verify_completion", kwargs={"pk": self.household.pk, "completion_pk": self.completion.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_completer_cannot_verify_own_completion(self):
        """User who completed the chore cannot verify their own completion."""
        self.client.login(username="member1", password="Password123!")
        response = self.client.post(
            reverse("chores:verify_completion", kwargs={"pk": self.household.pk, "completion_pk": self.completion.pk})
        )
        self.assertEqual(response.status_code, 403)
        self.completion.refresh_from_db()
        self.assertFalse(self.completion.verified)

    def test_other_member_verifies_completion(self):
        """Other household member can verify completion."""
        self.client.login(username="owner1", password="Password123!")
        response = self.client.post(
            reverse("chores:verify_completion", kwargs={"pk": self.household.pk, "completion_pk": self.completion.pk})
        )
        self.assertRedirects(response, reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.completion.refresh_from_db()
        self.assertTrue(self.completion.verified)

    def test_verifying_already_verified_is_idempotent(self):
        """Verifying an already-verified completion redirects cleanly without error."""
        self.completion.verified = True
        self.completion.save()

        self.client.login(username="owner1", password="Password123!")
        response = self.client.post(
            reverse("chores:verify_completion", kwargs={"pk": self.household.pk, "completion_pk": self.completion.pk})
        )
        self.assertRedirects(response, reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.completion.refresh_from_db()
        self.assertTrue(self.completion.verified)

    def test_board_shows_verify_button_only_to_non_completers(self):
        """Verify button appears on board for other members, but not for completer."""
        # Member who completed: no verify button
        self.client.login(username="member1", password="Password123!")
        response = self.client.get(reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertNotContains(response, f"/completions/{self.completion.pk}/verify/")

        # Owner (different member): verify button is present
        self.client.login(username="owner1", password="Password123!")
        response = self.client.get(reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertContains(response, f"/completions/{self.completion.pk}/verify/")

    def test_board_shows_verified_vs_unverified_badges(self):
        """Board shows unverified badge when false, and verified badge when true."""
        self.client.login(username="owner1", password="Password123!")
        response = self.client.get(reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertContains(response, "Done (unverified)")

        self.completion.verified = True
        self.completion.save()

        response = self.client.get(reverse("chores:board", kwargs={"pk": self.household.pk}))
        self.assertContains(response, "Done ✓ (verified)")


class CarryForwardChoresCommandTest(TestCase):
    """Tests for the carry_forward_chores management command."""

    def setUp(self):
        import io
        from django.core.management import call_command
        self.call_command = call_command
        self.StringIO = io.StringIO

        self.owner = User.objects.create_user(username="owner1", password="Password123!")
        self.household = Household.objects.create(name="Smith Family", owner=self.owner)
        self.member = User.objects.create_user(username="member1", password="Password123!")
        Membership.objects.create(household=self.household, user=self.owner)
        Membership.objects.create(household=self.household, user=self.member)

        # Chore due in the past relative to ref date 2026-11-05
        self.overdue_chore = Chore.objects.create(
            household=self.household,
            title="Overdue Dishes",
            frequency=Chore.Frequency.DAILY,
            point_value=5,
            next_due_date=date(2026, 11, 2),
            rotation_members=[self.member.pk],
        )
        # Chore due on reference date
        self.today_chore = Chore.objects.create(
            household=self.household,
            title="Today Laundry",
            frequency=Chore.Frequency.DAILY,
            point_value=10,
            next_due_date=date(2026, 11, 5),
            rotation_members=[self.owner.pk],
        )
        # Chore due in the future
        self.future_chore = Chore.objects.create(
            household=self.household,
            title="Future Garden",
            frequency=Chore.Frequency.WEEKLY,
            point_value=20,
            next_due_date=date(2026, 11, 10),
            rotation_members=[self.member.pk],
        )

    def test_overdue_chore_with_no_completion_is_flagged_without_changing_date(self):
        """Overdue chore with no completion is reported and due date is preserved."""
        out = self.StringIO()
        self.call_command("carry_forward_chores", date="2026-11-05", stdout=out)
        output = out.getvalue()
        self.assertIn("Overdue Dishes", output)
        self.assertIn("1 overdue chore(s) found", output)

        self.overdue_chore.refresh_from_db()
        self.assertEqual(self.overdue_chore.next_due_date, date(2026, 11, 2))

    def test_chore_with_completion_in_current_period_is_not_flagged(self):
        """Chore with completion for its period is not flagged as overdue."""
        # Create completion for overdue_chore
        completion = ChoreCompletion.objects.create(
            chore=self.overdue_chore,
            completed_by=self.member,
        )
        # Manually backdate completed_at to match period
        from django.utils import timezone
        ChoreCompletion.objects.filter(pk=completion.pk).update(
            completed_at=timezone.make_aware(datetime(2026, 11, 2, 12, 0))
        )

        out = self.StringIO()
        self.call_command("carry_forward_chores", date="2026-11-05", stdout=out)
        output = out.getvalue()
        self.assertNotIn("Overdue Dishes", output)

    def test_due_today_and_future_chores_are_not_flagged(self):
        """Chores due today or in future are not flagged as overdue."""
        out = self.StringIO()
        self.call_command("carry_forward_chores", date="2026-11-05", stdout=out)
        output = out.getvalue()
        self.assertNotIn("Today Laundry", output)
        self.assertNotIn("Future Garden", output)

    def test_command_is_idempotent(self):
        """Running the command multiple times produces identical output and changes nothing."""
        out1 = self.StringIO()
        self.call_command("carry_forward_chores", date="2026-11-05", stdout=out1)

        out2 = self.StringIO()
        self.call_command("carry_forward_chores", date="2026-11-05", stdout=out2)

        self.assertEqual(out1.getvalue(), out2.getvalue())
        self.overdue_chore.refresh_from_db()
        self.assertEqual(self.overdue_chore.next_due_date, date(2026, 11, 2))


class PointsTrackingTest(TestCase):
    """Tests for points awarding and verification bonus."""

    def setUp(self):
        from chores.points import award_completion_points, award_verification_bonus
        self.award_completion_points = award_completion_points
        self.award_verification_bonus = award_verification_bonus

        self.owner = User.objects.create_user(username="owner1", password="Password123!")
        self.member = User.objects.create_user(username="member1", password="Password123!")
        self.household = Household.objects.create(name="Smith Family", owner=self.owner)
        self.owner_membership = Membership.objects.create(household=self.household, user=self.owner)
        self.member_membership = Membership.objects.create(household=self.household, user=self.member)

        self.chore = Chore.objects.create(
            household=self.household,
            title="Clean Kitchen",
            frequency=Chore.Frequency.DAILY,
            point_value=25,
            next_due_date=date.today(),
            rotation_members=[self.member.pk],
        )

    def test_completion_awards_base_points(self):
        """Creating completion awards chore.point_value to completing member."""
        completion = ChoreCompletion.objects.create(
            chore=self.chore,
            completed_by=self.member,
        )
        self.award_completion_points(completion)

        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.points, 25)

    def test_verification_awards_ten_percent_floor_bonus(self):
        """Verifying completion awards floor(point_value * 0.10) to completing member."""
        completion = ChoreCompletion.objects.create(
            chore=self.chore,
            completed_by=self.member,
        )
        self.award_completion_points(completion)
        self.award_verification_bonus(completion)

        self.member_membership.refresh_from_db()
        # 25 + floor(25 * 0.10) = 25 + 2 = 27
        self.assertEqual(self.member_membership.points, 27)

    def test_small_point_value_bonus_rounds_down_to_zero(self):
        """point_value = 5 awards 0 bonus on verification."""
        small_chore = Chore.objects.create(
            household=self.household,
            title="Quick Task",
            frequency=Chore.Frequency.DAILY,
            point_value=5,
            next_due_date=date.today(),
        )
        completion = ChoreCompletion.objects.create(
            chore=small_chore,
            completed_by=self.member,
        )
        self.award_completion_points(completion)
        bonus = self.award_verification_bonus(completion)

        self.assertEqual(bonus, 0)
        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.points, 5)

    def test_point_values_10_and_100_bonuses(self):
        """point_value=10 gives bonus=1; point_value=100 gives bonus=10."""
        chore10 = Chore.objects.create(
            household=self.household,
            title="Task 10",
            frequency=Chore.Frequency.DAILY,
            point_value=10,
            next_due_date=date.today(),
        )
        comp10 = ChoreCompletion.objects.create(chore=chore10, completed_by=self.member)
        self.assertEqual(self.award_verification_bonus(comp10), 1)

        chore100 = Chore.objects.create(
            household=self.household,
            title="Task 100",
            frequency=Chore.Frequency.WEEKLY,
            point_value=100,
            next_due_date=date.today(),
        )
        comp100 = ChoreCompletion.objects.create(chore=chore100, completed_by=self.member)
        self.assertEqual(self.award_verification_bonus(comp100), 10)

    def test_points_are_cumulative_and_other_members_unaffected(self):
        """Points accumulate across completions; other members' points remain 0."""
        comp1 = ChoreCompletion.objects.create(chore=self.chore, completed_by=self.member)
        self.award_completion_points(comp1)

        comp2 = ChoreCompletion.objects.create(chore=self.chore, completed_by=self.member)
        self.award_completion_points(comp2)

        self.member_membership.refresh_from_db()
        self.owner_membership.refresh_from_db()

        self.assertEqual(self.member_membership.points, 50)
        self.assertEqual(self.owner_membership.points, 0)

    def test_integration_complete_and_verify_views_award_points(self):
        """Full view integration: completing via POST and verifying via POST awards points."""
        self.client.login(username="member1", password="Password123!")
        # Complete chore
        self.client.post(
            reverse("chores:complete_chore", kwargs={"pk": self.household.pk, "chore_pk": self.chore.pk})
        )
        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.points, 25)

        # Verify as owner
        completion = ChoreCompletion.objects.get(chore=self.chore)
        self.client.login(username="owner1", password="Password123!")
        self.client.post(
            reverse("chores:verify_completion", kwargs={"pk": self.household.pk, "completion_pk": completion.pk})
        )
        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.points, 27)








