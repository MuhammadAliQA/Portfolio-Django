import pytest


@pytest.mark.django_db
def test_register_then_login_with_username(api_client):
    register_response = api_client.post(
        "/api/users/register/",
        {
            "username": "pytest_register",
            "email": "pytest_register@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
            "role": "mentor",
        },
        format="json",
    )
    assert register_response.status_code == 201

    login_response = api_client.post(
        "/api/users/login/",
        {"username": "pytest_register", "password": "StrongPass123!"},
        format="json",
    )
    assert login_response.status_code == 200
    assert "access" in login_response.data
    assert login_response.data["user"]["role"] == "mentor"


@pytest.mark.django_db
def test_login_with_email(api_client, student):
    response = api_client.post(
        "/api/users/login/",
        {"username": student.email, "password": "StrongPass123!"},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["user"]["role"] == "student"
