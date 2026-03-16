from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from mentors.models import FavoriteMentor, MentorAvailability, MentorProfile
from users.models import User


class MentorApiTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student_mentor",
            email="student_mentor@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.mentor_user = User.objects.create_user(
            username="mentor_api",
            email="mentor_api@example.com",
            password="StrongPass123!",
            role="mentor",
            first_name="Ali",
            last_name="Karimov",
        )
        self.featured_user = User.objects.create_user(
            username="mentor_featured",
            email="mentor_featured@example.com",
            password="StrongPass123!",
            role="mentor",
        )
        self.mentor = MentorProfile.objects.create(
            user=self.mentor_user,
            expertise="IELTS Writing",
            primary_track="ielts",
            experience_years=4,
            price_per_hour=Decimal("35.00"),
            rating=4.8,
        )
        self.featured_mentor = MentorProfile.objects.create(
            user=self.featured_user,
            expertise="SAT Math",
            primary_track="sat",
            experience_years=5,
            price_per_hour=Decimal("45.00"),
            rating=4.9,
            is_featured=True,
        )

    def test_list_can_filter_by_max_price(self):
        res = self.client.get("/api/mentors/?max_price=40")
        self.assertEqual(res.status_code, 200)
        results = res.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["username"], "mentor_api")

    def test_featured_endpoint_returns_only_featured(self):
        res = self.client.get("/api/mentors/featured/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["username"], "mentor_featured")

    def test_availability_returns_only_open_slots(self):
        MentorAvailability.objects.create(
            mentor=self.mentor,
            date=timezone.localdate() + timedelta(days=2),
            time=timezone.now().time().replace(hour=10, minute=0, second=0, microsecond=0),
            is_available=True,
        )
        MentorAvailability.objects.create(
            mentor=self.mentor,
            date=timezone.localdate() + timedelta(days=3),
            time=timezone.now().time().replace(hour=11, minute=0, second=0, microsecond=0),
            is_available=False,
        )
        res = self.client.get(f"/api/mentors/{self.mentor.id}/availability/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertTrue(res.data[0]["is_available"])

    def test_authenticated_user_can_toggle_favorite(self):
        self.client.force_authenticate(user=self.student)
        save_res = self.client.post(f"/api/mentors/{self.mentor.id}/favorite/")
        self.assertEqual(save_res.status_code, 200)
        self.assertEqual(save_res.data["status"], "saved")
        self.assertTrue(FavoriteMentor.objects.filter(user=self.student, mentor=self.mentor).exists())

        remove_res = self.client.post(f"/api/mentors/{self.mentor.id}/favorite/")
        self.assertEqual(remove_res.status_code, 200)
        self.assertEqual(remove_res.data["status"], "removed")
        self.assertFalse(FavoriteMentor.objects.filter(user=self.student, mentor=self.mentor).exists())

    def test_anonymous_user_cannot_favorite(self):
        res = self.client.post(f"/api/mentors/{self.mentor.id}/favorite/")
        self.assertEqual(res.status_code, 401)


class MentorPageTests(TestCase):
    def test_public_pages_render(self):
        urls = [
            "/",
            "/mentors/",
            "/lessons/",
            "/mock-tests/",
            "/login/",
            "/register/",
            "/faq/",
            "/information/",
            "/sitemap/",
            "/student-dashboard/",
            "/mentor-dashboard/",
        ]
        for url in urls:
            with self.subTest(url=url):
                res = self.client.get(url)
                self.assertEqual(res.status_code, 200)
