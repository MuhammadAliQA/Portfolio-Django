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

    def test_submit_with_wrong_choice_returns_400(self):
        self.client.force_authenticate(user=self.user)
        # Create a choice belonging to another question
        other_exam = Exam.objects.create(title="Other Exam", track="sat", is_published=True)
        other_question = Question.objects.create(exam=other_exam, prompt="Other prompt", order=1, points=1)
        wrong_choice = Choice.objects.create(question=other_question, text="wrong", is_correct=True, order=1)

        res = self.client.post(
            f"/api/assessments/exams/{self.exam.id}/submit/",
            {"answers": [{"question": self.question.id, "choice": wrong_choice.id}]},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.data)

    def test_submit_empty_answers(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(
            f"/api/assessments/exams/{self.exam.id}/submit/",
            {"answers": []},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        attempt = Attempt.objects.get(user=self.user, exam=self.exam)
        self.assertEqual(attempt.score, 0)
        self.assertEqual(float(attempt.percentage), 0.0)

    def test_submit_partial_correct_answers(self):
        self.client.force_authenticate(user=self.user)
        # Add another question to the exam
        q2 = Question.objects.create(exam=self.exam, prompt="Second question", order=2, points=2)
        q2_correct = Choice.objects.create(question=q2, text="right", is_correct=True, order=1)
        q2_wrong = Choice.objects.create(question=q2, text="wrong", is_correct=False, order=2)

        res = self.client.post(
            f"/api/assessments/exams/{self.exam.id}/submit/",
            {"answers": [
                {"question": self.question.id, "choice": self.correct_choice.id},
                {"question": q2.id, "choice": q2_wrong.id}
            ]},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        attempt = Attempt.objects.get(user=self.user, exam=self.exam)
        self.assertEqual(attempt.score, 2)
        self.assertEqual(attempt.max_score, 4)
        self.assertEqual(float(attempt.percentage), 50.0)
