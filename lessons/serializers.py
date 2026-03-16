from rest_framework import serializers
from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(read_only=True)
    track_label = serializers.CharField(read_only=True)
    protected_asset_url = serializers.SerializerMethodField()
    can_download_material = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "description",
            "track",
            "track_label",
            "file",
            "video_url",
            "protected_asset_url",
            "can_download_material",
            "is_published",
            "created_by",
            "creator_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        file_obj = attrs.get("file", getattr(instance, "file", None))
        video_url = attrs.get("video_url", getattr(instance, "video_url", ""))

        if not file_obj and not video_url:
            raise serializers.ValidationError(
                "Lesson uchun video link yoki video/fayl yuklanishi kerak."
            )
        return attrs

    def get_protected_asset_url(self, obj):
        if not obj.file:
            return ""
        return f"/api/lessons/{obj.id}/asset/"

    def get_can_download_material(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return user.is_staff or getattr(user, "role", "") == "mentor"
