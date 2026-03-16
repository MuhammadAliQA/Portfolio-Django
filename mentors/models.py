from django.db import models

from users.models import User


class MentorProfile(models.Model):
    TRACK_CHOICES = (
        ("ielts", "IELTS"),
        ("sat", "SAT"),
        ("admission", "Admission"),
        ("strategy", "Study Strategy"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expertise = models.CharField(max_length=200)
    primary_track = models.CharField(
        max_length=20,
        choices=TRACK_CHOICES,
        default="ielts",
    )
    headline = models.CharField(max_length=255, blank=True)
    university_background = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=120, blank=True)
    about = models.TextField(blank=True)
    experience_years = models.IntegerField()
    students_helped = models.PositiveIntegerField(default=0)
    success_story_count = models.PositiveIntegerField(default=0)
    offers_admission_support = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.user.username


class MentorAvailability(models.Model):
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.mentor} {self.date} {self.time}"

    class Meta:
        ordering = ("date", "time")
        unique_together = ("mentor", "date", "time")


class FavoriteMentor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "mentor")
