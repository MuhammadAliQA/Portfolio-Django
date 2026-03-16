import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    [
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
    ],
)
def test_public_pages_render(client, url):
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_lessons_api_lists_published_only(api_client, published_lesson):
    response = api_client.get("/api/lessons/")
    assert response.status_code == 200
    assert response.data["results"][0]["title"] == published_lesson.title
