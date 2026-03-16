from rest_framework import serializers
from .models import MentorProfile, MentorAvailability


class MentorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = MentorAvailability
        fields = ['id', 'date', 'time', 'is_available']


class MentorSerializer(serializers.ModelSerializer):
    full_name            = serializers.CharField(source='user.get_full_name', read_only=True)
    username             = serializers.CharField(source='user.username',      read_only=True)
    avatar               = serializers.ImageField(source='user.avatar',       read_only=True)
    track_label          = serializers.CharField(source='get_primary_track_display', read_only=True)
    available_slots      = MentorAvailabilitySerializer(
        source='mentoravailability_set',
        many=True, read_only=True
    )

    class Meta:
        model  = MentorProfile
        fields = [
            'id', 'full_name', 'username', 'avatar',
            'expertise', 'primary_track', 'track_label',
            'headline', 'university_background', 'languages',
            'about', 'experience_years', 'students_helped',
            'success_story_count', 'offers_admission_support',
            'is_featured', 'price_per_hour', 'rating',
            'available_slots',
        ]