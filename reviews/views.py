from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from django.db.models import Avg
from .models import Review
from .serializers import ReviewSerializer
from consultations.models import Consultation


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class   = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Review.objects.select_related('mentor', 'student')
        mentor_id = self.request.query_params.get('mentor')
        if mentor_id:
            qs = qs.filter(mentor_id=mentor_id)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        mentor = serializer.validated_data['mentor']
        student = self.request.user

        # Faqat sessiya o'tkazgan student review yoza oladi
        has_session = Consultation.objects.filter(
            student=student, mentor=mentor, status='completed'
        ).exists()
        if not has_session:
            raise ValidationError("Faqat yakunlangan sessiyadan so'ng review yozing.")

        # Bir mentorga faqat bir marta review
        if Review.objects.filter(mentor=mentor, student=student).exists():
            raise ValidationError("Siz bu mentor uchun allaqachon review yozgansiz.")

        review = serializer.save(student=student)

        # Mentor ratingini yangilash
        avg = Review.objects.filter(mentor=mentor).aggregate(v=Avg('rating'))['v'] or 0
        mentor.rating = round(avg, 2)
        mentor.save(update_fields=['rating'])