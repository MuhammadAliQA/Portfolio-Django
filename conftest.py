import pytest
from rest_framework.test import APIClient

from assessments.models import Choice, Exam, Question
from lessons.models import Lesson
from mentors.models import MentorProfile
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student(db):
    return User.objects.create_user(
        username="pytest_student",
        email="pytest_student@example.com",
        password="StrongPass123!",
        role="student",
        first_name="Py",
        last_name="Student",
    )


@pytest.fixture
def mentor_user(db):
    return User.objects.create_user(
        username="pytest_mentor",
        email="pytest_mentor@example.com",
        password="StrongPass123!",
        role="mentor",
        first_name="Py",
        last_name="Mentor",
    )


@pytest.fixture
def mentor_profile(db, mentor_user):
    return MentorProfile.objects.create(
        user=mentor_user,
        expertise="IELTS Writing",
        primary_track="ielts",
        experience_years=5,
        rating=4.9,
    )


@pytest.fixture
def published_lesson(db, mentor_user):
    return Lesson.objects.create(
        title="Pytest IELTS Lesson",
        description="Published fixture lesson",
        track="ielts",
        video_url="https://example.com/pytest-lesson",
        created_by=mentor_user,
        is_published=True,
    )


@pytest.fixture
def mock_exam(db):
    exam = Exam.objects.create(
        title="Pytest Mock Exam",
        track="ielts",
        section="Reading",
        description="Fixture exam",
        duration_minutes=20,
        is_published=True,
    )
    question = Question.objects.create(
        exam=exam,
        prompt="Select the correct answer.",
        context_text="A short reading passage for the fixture exam.",
        order=1,
        points=2,
    )
    Choice.objects.create(question=question, text="Correct", is_correct=True, order=1)
    Choice.objects.create(question=question, text="Wrong", is_correct=False, order=2)
    return exam
