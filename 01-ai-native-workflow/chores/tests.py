from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


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

