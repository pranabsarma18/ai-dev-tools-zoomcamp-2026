from datetime import date
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from chores.models import Household, Membership, Chore


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


