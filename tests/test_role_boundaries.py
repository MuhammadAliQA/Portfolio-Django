import pytest


@pytest.mark.django_db
def test_student_cannot_create_lesson(api_client, student):
    api_client.force_authenticate(user=student)
    response = api_client.post(
        "/api/lessons/",
        {"title": "Forbidden lesson", "track": "sat"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_mentor_can_create_lesson(api_client, mentor_user):
    api_client.force_authenticate(user=mentor_user)
    response = api_client.post(
        "/api/lessons/",
        {
            "title": "Mentor lesson",
            "description": "Created via pytest",
            "track": "ielts",
            "video_url": "https://example.com/mentor-lesson",
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.data["title"] == "Mentor lesson"


@pytest.mark.django_db
def test_mock_submit_requires_auth(api_client, mock_exam):
    question = mock_exam.questions.first()
    choice = question.choices.filter(is_correct=True).first()
    response = api_client.post(
        f"/api/assessments/exams/{mock_exam.id}/submit/",
        {"answers": [{"question": question.id, "choice": choice.id}]},
        format="json",
    )
    assert response.status_code == 401
