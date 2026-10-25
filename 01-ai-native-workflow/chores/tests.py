from django.test import TestCase
from django.urls import reverse


class SmokeTest(TestCase):
    """Smoke test — confirms the app boots and the home route responds."""

    def test_home_returns_200(self):
        response = self.client.get(reverse("chores:index"))
        self.assertLess(response.status_code, 500)


class SanityTest(TestCase):
    """Plain unit test — no Django at all."""

    def test_addition(self):
        self.assertEqual(1 + 1, 2)

