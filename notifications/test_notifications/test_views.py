# notifications/tests/test_views.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

from notifications.models import Notification

class NotificationViewsTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(
            username="u1", email="u1@example.com", password="pass"
        )
        self.user2 = User.objects.create_user(
            username="u2", email="u2@example.com", password="pass"
        )
        # u1 gets two, u2 gets one
        Notification.objects.create(recipient=self.user1, verb="First")
        Notification.objects.create(recipient=self.user2, verb="Solo")
        Notification.objects.create(recipient=self.user1, verb="Second")

        self.client = APIClient()
        self.url = reverse("notifications:list")

    def test_list_returns_only_authenticated_user_notifications(self):
        self.client.force_authenticate(self.user1)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # should return 2 notifications, newest first
        verbs = [n["verb"] for n in data]
        self.assertEqual(verbs, ["Second", "First"])

    def test_unauthenticated_get_is_denied(self):
        resp = self.client.get(self.url)
        # DRF's IsAuthenticated returns 401 for unauthenticated
        self.assertEqual(resp.status_code, 401)
