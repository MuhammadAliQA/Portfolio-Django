import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from lessons.models import Lesson


class LessonApiTests(APITestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def setUp(self):
        self.mentor = User.objects.create_user(
            username="mentor2",
            email="mentor2@example.com",
            password="StrongPass123!",
            role="mentor",
        )
        self.student = User.objects.create_user(
            username="student2",
            email="student2@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.other_mentor = User.objects.create_user(
            username="mentor3",
            email="mentor3@example.com",
            password="StrongPass123!",
            role="mentor",
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.override = override_settings(MEDIA_ROOT=cls.TEMP_MEDIA_ROOT)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        super().tearDownClass()
        shutil.rmtree(cls.TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_mentor_can_create_lesson(self):
        self.client.force_authenticate(user=self.mentor)
        res = self.client.post(
            "/api/lessons/",
            {
                "title": "IELTS Speaking Basics",
                "description": "Core speaking structure and scoring criteria.",
                "track": "ielts",
                "video_url": "https://example.com/video",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_student_cannot_create_lesson(self):
        self.client.force_authenticate(user=self.student)
        res = self.client.post(
            "/api/lessons/",
            {"title": "SAT Math", "track": "sat"},
            format="json",
        )
        self.assertEqual(res.status_code, 403)

    def test_anonymous_only_sees_published(self):
        Lesson.objects.create(title="IELTS", track="ielts", is_published=True)
        Lesson.objects.create(title="SAT draft", track="sat", is_published=False)
        res = self.client.get("/api/lessons/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.data)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], "IELTS")

    def test_mentor_can_upload_video_file(self):
        self.client.force_authenticate(user=self.mentor)
        video = SimpleUploadedFile(
            "lesson.mp4",
            b"fake-video-content",
            content_type="video/mp4",
        )
        res = self.client.post(
            "/api/lessons/",
            {
                "title": "SAT Timed Drill",
                "description": "Timed practice walkthrough.",
                "track": "sat",
                "file": video,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, 201)
        self.assertTrue(Lesson.objects.filter(title="SAT Timed Drill").exists())

    def test_lesson_requires_video_or_file(self):
        self.client.force_authenticate(user=self.mentor)
        res = self.client.post(
            "/api/lessons/",
            {
                "title": "Empty lesson",
                "description": "Draft without media.",
                "track": "ielts",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_other_mentor_cannot_edit_foreign_lesson(self):
        lesson = Lesson.objects.create(
            title="IELTS Writing Task 2",
            track="ielts",
            video_url="https://example.com/video",
            created_by=self.mentor,
        )
        self.client.force_authenticate(user=self.other_mentor)
        res = self.client.patch(
            f"/api/lessons/{lesson.id}/",
            {"title": "Changed"},
            format="json",
        )
        self.assertEqual(res.status_code, 403)

    def test_mine_query_only_returns_own_lessons_for_mentor(self):
        Lesson.objects.create(
            title="Own lesson",
            track="ielts",
            video_url="https://example.com/own",
            created_by=self.mentor,
        )
        Lesson.objects.create(
            title="Foreign published",
            track="sat",
            video_url="https://example.com/foreign",
            created_by=self.other_mentor,
            is_published=True,
        )
        self.client.force_authenticate(user=self.mentor)
        res = self.client.get("/api/lessons/?mine=1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], "Own lesson")

    def test_owner_can_delete_lesson(self):
        lesson = Lesson.objects.create(
            title="Delete me",
            track="ielts",
            video_url="https://example.com/delete",
            created_by=self.mentor,
        )
        self.client.force_authenticate(user=self.mentor)
        res = self.client.delete(f"/api/lessons/{lesson.id}/")
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Lesson.objects.filter(id=lesson.id).exists())

    def test_student_can_stream_video_asset(self):
        lesson = Lesson.objects.create(
            title="IELTS Video",
            track="ielts",
            created_by=self.mentor,
            file=SimpleUploadedFile("stream.mp4", b"fake-video", content_type="video/mp4"),
            is_published=True,
        )
        token = str(RefreshToken.for_user(self.student).access_token)
        res = self.client.get(f"/api/lessons/{lesson.id}/asset/?token={token}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("inline", res["Content-Disposition"])

    def test_student_cannot_open_non_video_material(self):
        lesson = Lesson.objects.create(
            title="SAT PDF",
            track="sat",
            created_by=self.mentor,
            file=SimpleUploadedFile("guide.pdf", b"%PDF-1.4", content_type="application/pdf"),
            is_published=True,
        )
        token = str(RefreshToken.for_user(self.student).access_token)
        res = self.client.get(f"/api/lessons/{lesson.id}/asset/?token={token}")
        self.assertEqual(res.status_code, 403)

    def test_mentor_can_open_non_video_material(self):
        lesson = Lesson.objects.create(
            title="Mentor PDF",
            track="sat",
            created_by=self.mentor,
            file=SimpleUploadedFile("mentor-guide.pdf", b"%PDF-1.4", content_type="application/pdf"),
            is_published=False,
        )
        token = str(RefreshToken.for_user(self.mentor).access_token)
        res = self.client.get(f"/api/lessons/{lesson.id}/asset/?token={token}")
        self.assertEqual(res.status_code, 200)
