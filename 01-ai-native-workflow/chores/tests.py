from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from chores.models import Household


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
