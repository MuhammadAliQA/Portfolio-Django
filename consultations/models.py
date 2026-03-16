from django.db import models
from django.utils import timezone

from mentors.models import MentorProfile
from users.models import User


class Consultation(models.Model):
    SERVICE_CHOICES = (
        ("ielts_plan", "IELTS Plan"),
        ("sat_plan", "SAT Plan"),
        ("admission", "Admission Support"),
        ("essay", "Essay Review"),
        ("career", "Career Mapping"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_CHOICES,
        default="ielts_plan",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    duration_minutes = models.PositiveIntegerField(default=60)
    goals = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_free_intro_call = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-date", "-time")
