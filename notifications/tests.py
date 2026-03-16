from django.test import TestCase

from notifications.models import Notification
from users.models import User


class NotificationModelTests(TestCase):
    def test_notification_defaults_to_unread(self):
        user = User.objects.create_user(
            username="notify_user",
            email="notify@example.com",
            password="StrongPass123!",
            role="student",
        )
        notification = Notification.objects.create(
            user=user,
            message="Your consultation was confirmed.",
        )
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.message, "Your consultation was confirmed.")
