from django.db import models
from users.models import User
from mentors.models import MentorProfile


class Review(models.Model):

    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE)

    student = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)