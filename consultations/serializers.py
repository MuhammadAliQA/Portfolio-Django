from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import serializers
from mentors.models import MentorAvailability
from .models import Consultation


class ConsultationSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source="mentor.user.get_full_name", read_only=True)
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)

    class Meta:
        model = Consultation
        fields = '__all__'
        read_only_fields = ("student", "status", "created_at")

    def validate(self, attrs):
        date = attrs.get("date") or getattr(self.instance, "date", None)
        time = attrs.get("time") or getattr(self.instance, "time", None)
        mentor = attrs.get("mentor") or getattr(self.instance, "mentor", None)
        duration = attrs.get("duration_minutes") or getattr(self.instance, "duration_minutes", 60)

        if not all([date, time, mentor]):
            return attrs

        starts_at = timezone.make_aware(datetime.combine(date, time))
        if starts_at <= timezone.now():
            raise serializers.ValidationError({"date": "Consultation must be scheduled in the future."})

        availability = MentorAvailability.objects.filter(
            mentor=mentor,
            date=date,
            time=time,
        ).first()
        if availability and not availability.is_available:
            raise serializers.ValidationError({"time": "This mentor is not available at the selected time."})

        ends_at = starts_at + timedelta(minutes=duration)
        queryset = Consultation.objects.filter(
            mentor=mentor,
            date=date,
            status__in=("pending", "confirmed"),
        ).exclude(pk=getattr(self.instance, "pk", None))

        for consultation in queryset:
            existing_start = timezone.make_aware(datetime.combine(consultation.date, consultation.time))
            existing_end = existing_start + timedelta(minutes=consultation.duration_minutes)
            if starts_at < existing_end and ends_at > existing_start:
                raise serializers.ValidationError({"time": "This time slot is already booked for the mentor."})

        student = self.context["request"].user
        student_queryset = Consultation.objects.filter(
            student=student,
            date=date,
            status__in=("pending", "confirmed"),
        ).exclude(pk=getattr(self.instance, "pk", None))
        for consultation in student_queryset:
            existing_start = timezone.make_aware(datetime.combine(consultation.date, consultation.time))
            existing_end = existing_start + timedelta(minutes=consultation.duration_minutes)
            if starts_at < existing_end and ends_at > existing_start:
                raise serializers.ValidationError({"time": "You already have another consultation at this time."})

        return attrs
