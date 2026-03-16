from datetime import time, timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from consultations.models import Consultation
from mentors.models import MentorProfile
from reviews.models import Review
from users.models import User


class ReviewApiTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="review_student",
            email="review_student@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.other_student = User.objects.create_user(
            username="review_student_2",
            email="review_student_2@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.mentor_user = User.objects.create_user(
            username="review_mentor",
            email="review_mentor@example.com",
            password="StrongPass123!",
            role="mentor",
        )
        self.mentor = MentorProfile.objects.create(
            user=self.mentor_user,
            expertise="Admission",
            primary_track="admission",
            experience_years=6,
            price_per_hour=Decimal("55.00"),
        )
        Consultation.objects.create(
            student=self.student,
            mentor=self.mentor,
            date=timezone.localdate() - timedelta(days=2),
            time=time(10, 0),
            duration_minutes=60,
            status="completed",
        )

    def test_student_with_completed_consultation_can_create_review(self):
        self.client.force_authenticate(user=self.student)
        res = self.client.post(
            "/api/reviews/",
            {
                "mentor": self.mentor.id,
                "rating": 5,
                "comment": "Very structured session.",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Review.objects.count(), 1)
        self.mentor.refresh_from_db()
        self.assertEqual(self.mentor.rating, 5.0)

    def test_student_without_completed_consultation_cannot_review(self):
        self.client.force_authenticate(user=self.other_student)
        res = self.client.post(
            "/api/reviews/",
            {
                "mentor": self.mentor.id,
                "rating": 4,
                "comment": "Trying without session.",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Review.objects.count(), 0)

    def test_duplicate_review_is_rejected(self):
        Review.objects.create(
            mentor=self.mentor,
            student=self.student,
            rating=5,
            comment="First review",
        )
        self.client.force_authenticate(user=self.student)
        res = self.client.post(
            "/api/reviews/",
            {
                "mentor": self.mentor.id,
                "rating": 4,
                "comment": "Second review",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_list_can_filter_by_mentor(self):
        Review.objects.create(
            mentor=self.mentor,
            student=self.student,
            rating=5,
            comment="Helpful",
        )
        res = self.client.get(f"/api/reviews/?mentor={self.mentor.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)
