from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import User


class AuthTests(APITestCase):
    def test_register_and_login(self):
        res = self.client.post(
            "/api/users/register/",
            {
                "username": "mentor1",
                "email": "mentor1@example.com",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
                "role": "mentor",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        login_res = self.client.post(
            "/api/users/login/",
            {"username": "mentor1", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("access", login_res.data)

    def test_login_with_email(self):
        user = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.assertTrue(user.is_active)
        login_res = self.client.post(
            "/api/users/login/",
            {"username": "student1@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(login_res.status_code, 200)
