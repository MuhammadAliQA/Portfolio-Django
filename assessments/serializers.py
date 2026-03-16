from rest_framework import serializers

from .models import Answer, Attempt, Choice, Exam, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "order"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "context_text", "prompt", "order", "points", "choices"]


class ExamListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    track_label = serializers.CharField(source="get_track_display", read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "track",
            "track_label",
            "section",
            "description",
            "level",
            "duration_minutes",
            "question_count",
        ]

    def get_question_count(self, obj):
        return obj.questions.count()


class ExamDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    track_label = serializers.CharField(source="get_track_display", read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "track",
            "track_label",
            "section",
            "description",
            "level",
            "duration_minutes",
            "questions",
        ]


class AnswerInputSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    choice = serializers.IntegerField()


class ExamSubmissionSerializer(serializers.Serializer):
    answers = AnswerInputSerializer(many=True)

    def validate_answers(self, value):
        question_ids = [item["question"] for item in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError("Bir savolga bir martadan ko'p javob yuborildi.")
        return value


class AttemptSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    track = serializers.CharField(source="exam.track", read_only=True)
    track_label = serializers.CharField(source="exam.get_track_display", read_only=True)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "exam",
            "exam_title",
            "track",
            "track_label",
            "score",
            "max_score",
            "percentage",
            "created_at",
        ]


class AttemptResultSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    track_label = serializers.CharField(source="exam.get_track_display", read_only=True)

    class Meta:
        model = Attempt
        fields = ["id", "exam", "exam_title", "track_label", "score", "max_score", "percentage", "created_at"]
