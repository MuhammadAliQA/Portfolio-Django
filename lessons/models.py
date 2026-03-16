from django.conf import settings
from django.db import models


class Lesson(models.Model):
    TRACK_CHOICES = (
        ("ielts", "IELTS"),
        ("sat", "SAT"),
    )

    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    track = models.CharField(max_length=20, choices=TRACK_CHOICES)
    file = models.FileField(upload_to="lessons/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.track})"

    @property
    def track_label(self):
        return self.get_track_display()

    @property
    def creator_name(self):
        if not self.created_by:
            return "EduBridge"
        return self.created_by.get_full_name()

    @property
    def is_video_file(self):
        if not self.file:
            return False
        name = self.file.name.lower()
        return name.endswith((".mp4", ".webm", ".mov", ".m4v", ".ogg"))

    @property
    def embed_video_url(self):
        if not self.video_url:
            return ""
        if "youtube.com/watch?v=" in self.video_url:
            return self.video_url.replace("watch?v=", "embed/")
        if "youtu.be/" in self.video_url:
            video_id = self.video_url.rstrip("/").split("/")[-1]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.video_url
