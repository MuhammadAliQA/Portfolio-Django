from datetime import time, timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APITestCase
from users.models import User
from mentors.models import MentorProfile, MentorAvailability
from consultations.models import Consultation
from payments.models import Payment


class ConsultationFlowTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student_booking",
            email="student_booking@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.mentor_user = User.objects.create_user(
            username="mentor_booking",
            email="mentor_booking@example.com",
            password="StrongPass123!",
            role="mentor",
        )
        self.mentor = MentorProfile.objects.create(
            user=self.mentor_user,
            expertise="IELTS",
            primary_track="ielts",
            experience_years=3,
            price_per_hour=Decimal("30.00"),
        )
        self.future_date = timezone.localdate() + timedelta(days=2)
        self.future_time = time(10, 0)

    def test_booking_creates_pending_payment(self):
        self.client.force_authenticate(user=self.student)
        res = self.client.post(
            "/api/consultations/",
            {
                "mentor": self.mentor.id,
                "date": self.future_date,
                "time": self.future_time,
                "duration_minutes": 60,
                "service_type": "ielts_plan",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        consultation = Consultation.objects.get()
        payment = Payment.objects.get(consultation=consultation)
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.amount, Decimal("30.00"))

    def test_overlapping_booking_is_rejected(self):
        Consultation.objects.create(
            student=self.student,
            mentor=self.mentor,
            date=self.future_date,
            time=self.future_time,
            duration_minutes=60,
            status="confirmed",
        )
        self.client.force_authenticate(user=self.student)
        res = self.client.post(
            "/api/consultations/",
            {
                "mentor": self.mentor.id,
                "date": self.future_date,
                "time": self.future_time,
                "duration_minutes": 60,
                "service_type": "ielts_plan",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_mentor_cannot_confirm_until_paid(self):
        consultation = Consultation.objects.create(
            student=self.student,
            mentor=self.mentor,
            date=self.future_date,
            time=self.future_time,
            duration_minutes=60,
            status="pending",
        )
        Payment.objects.create(
            user=self.student,
            consultation=consultation,
            amount=Decimal("30.00"),
            status="pending",
        )
        self.client.force_authenticate(user=self.mentor_user)
        res = self.client.post(f"/api/consultations/{consultation.id}/confirm/")
        self.assertEqual(res.status_code, 400)
        consultation.refresh_from_db()
        self.assertEqual(consultation.status, "pending")

    def test_unavailable_slot_is_rejected(self):
        MentorAvailability.objects.create(
            mentor=self.mentor,
            date=self.future_date,
            time=self.future_time,
            is_available=False,
        )
        self.client.force_authenticate(user=self.student)
        res = self.client.post(
            "/api/consultations/",
            {
                "mentor": self.mentor.id,
                "date": self.future_date,
                "time": self.future_time,
                "duration_minutes": 60,
                "service_type": "ielts_plan",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)
