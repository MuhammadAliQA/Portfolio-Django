from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assessments.models import Attempt, Choice, Exam, Question


class AssessmentApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="mock_student",
            email="mock@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.exam = Exam.objects.create(
            title="IELTS Mini Mock",
            track="ielts",
            section="Reading",
            description="Short test",
            duration_minutes=15,
            is_published=True,
        )
        self.question = Question.objects.create(exam=self.exam, prompt="Choose the synonym of 'tiny'.", order=1, points=2)
        self.correct_choice = Choice.objects.create(question=self.question, text="small", is_correct=True, order=1)
        self.wrong_choice = Choice.objects.create(question=self.question, text="loud", is_correct=False, order=2)

    def test_public_can_list_exams(self):
        res = self.client.get("/api/assessments/exams/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data["results"]), 1)

    def test_public_can_view_exam_detail(self):
        res = self.client.get(f"/api/assessments/exams/{self.exam.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["questions"]), 1)

    def test_authenticated_user_can_submit_exam(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(
            f"/api/assessments/exams/{self.exam.id}/submit/",
            {"answers": [{"question": self.question.id, "choice": self.correct_choice.id}]},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        attempt = Attempt.objects.get(user=self.user, exam=self.exam)
        self.assertEqual(attempt.score, 2)
        self.assertEqual(float(attempt.percentage), 100.0)

    def test_submit_requires_login(self):
        res = self.client.post(
            f"/api/assessments/exams/{self.exam.id}/submit/",
            {"answers": [{"question": self.question.id, "choice": self.correct_choice.id}]},
            format="json",
        )
        self.assertEqual(res.status_code, 401)

    def test_user_can_view_own_attempts(self):
        Attempt.objects.create(user=self.user, exam=self.exam, score=1, max_score=2, percentage=50)
        self.client.force_authenticate(user=self.user)
        res = self.client.get("/api/assessments/attempts/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)
