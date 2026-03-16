from datetime import time, timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APITestCase
from users.models import User
from mentors.models import MentorProfile
from consultations.models import Consultation
from payments.models import Payment


class PaymentFlowTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student_pay",
            email="student_pay@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.mentor_user = User.objects.create_user(
            username="mentor_pay",
            email="mentor_pay@example.com",
            password="StrongPass123!",
            role="mentor",
        )
        self.mentor = MentorProfile.objects.create(
            user=self.mentor_user,
            expertise="SAT",
            primary_track="sat",
            experience_years=4,
            price_per_hour=Decimal("40.00"),
        )
        self.consultation = Consultation.objects.create(
            student=self.student,
            mentor=self.mentor,
            date=timezone.localdate() + timedelta(days=3),
            time=time(11, 0),
            duration_minutes=60,
            status="pending",
        )
        self.payment = Payment.objects.create(
            user=self.student,
            consultation=self.consultation,
            amount=Decimal("40.00"),
            status="pending",
        )

    def test_student_can_complete_own_payment(self):
        self.client.force_authenticate(user=self.student)
        res = self.client.post(f"/api/payments/{self.payment.id}/complete/")
        self.assertEqual(res.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "paid")
        self.assertIsNotNone(self.payment.paid_at)

    def test_mentor_can_confirm_after_payment(self):
        self.payment.status = "paid"
        self.payment.paid_at = timezone.now()
        self.payment.save(update_fields=["status", "paid_at"])
        self.client.force_authenticate(user=self.mentor_user)
        res = self.client.post(f"/api/consultations/{self.consultation.id}/confirm/")
        self.assertEqual(res.status_code, 200)
        self.consultation.refresh_from_db()
        self.assertEqual(self.consultation.status, "confirmed")
