from django.test import TestCase
from django.contrib.auth import get_user_model
from notifications.models import Notification

class NotificationModelTest(TestCase):
    def test_str_returns_recipient_email_and_verb(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="tester", email="tester@example.com", password="pass"
        )
        n = Notification.objects.create(
            recipient=user,
            verb="Performed an action",
            data={"foo": "bar"},
            link="http://example.com",
            unread=True,
        )
        self.assertEqual(str(n), "tester@example.com: Performed an action")
